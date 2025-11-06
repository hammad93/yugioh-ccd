import sys
import sqlite3
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton,
    QListWidget, QLabel, QSpinBox, QTextEdit, QFileDialog, QMessageBox, 
    QTabWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QAbstractItemView,
    QProgressDialog
)
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt
import pandas as pd
import os
import openpyxl
import traceback
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtNetwork import QNetworkReply
import signal

class YGOInventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YGO Inventory Manager")
        self.inventory = []
        self.setGeometry(100, 100, 800, 600)
        
        # Begin card image code
        # Network manager for loading images
        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.on_image_loaded)
        
        # Add image label and disclaimer to main tab layout
        main_widget = self.create_main_tab()
        layout = main_widget.layout()
        layout.addWidget(self.image_label)
        # End card image code

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(main_widget, "Main")
        self.tab_widget.addTab(self.create_inventory_tab(), "Inventory")
        
        self.central_widget.setLayout(QVBoxLayout())
        self.central_widget.layout().addWidget(self.tab_widget)
        
        if not os.path.exists('ygo_inventory.db'):
            QMessageBox.critical(self, "Database Error", "SQLite database does not exist. Please ensure it is present and try again.")
            sys.exit(1)
        
        self.default_filename = "ygo_inventory.xlsx"
        
        self.conn = sqlite3.connect('ygo_inventory.db')
        self.cursor = self.conn.cursor()
    
    def create_main_tab(self):
        main_widget = QWidget()
        layout = QHBoxLayout()  # Use QHBoxLayout to place elements side by side
        main_widget.setLayout(layout)
        
        # Left side: Search and results
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Press enter to search for card / product name...")
        self.search_bar.returnPressed.connect(self.search_database)
        left_layout.addWidget(self.search_bar)
        
        self.results_list = QListWidget()
        self.results_list.currentRowChanged.connect(self.on_selection_changed)
        left_layout.addWidget(self.results_list)
        
        self.select_button = QPushButton("Add to Inventory")
        self.select_button.clicked.connect(self.update_inventory)
        self.select_button.setShortcut(QKeySequence("Shift+Return"))
        left_layout.addWidget(self.select_button)
        
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 100)
        left_layout.addWidget(QLabel("Quantity:"))
        left_layout.addWidget(self.quantity_spinbox)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Notes (1st Edition, Unlimited, misprint, etc.). This field is required.")
        left_layout.addWidget(QLabel("Notes:"))
        left_layout.addWidget(self.notes_edit)
        
        self.save_button = QPushButton("Save to Spreadsheet")
        self.save_button.clicked.connect(self.save_to_spreadsheet)
        left_layout.addWidget(self.save_button)
        
        self.update_prices_button = QPushButton("Update prices in Spreadsheet")
        self.update_prices_button.clicked.connect(self.update_spreadsheet_prices)
        left_layout.addWidget(self.update_prices_button)
        
        layout.addWidget(left_widget)
        
        # Right side: Image display
        self.image_label = QLabel("Selected image will appear here, loaded from TCGPlayer")
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        right_layout.addWidget(self.image_label)
        
        layout.addWidget(right_widget)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(main_widget, "Main")
        self.tab_widget.addTab(self.create_inventory_tab(), "Inventory")
        
        self.central_widget.setLayout(QVBoxLayout())
        self.central_widget.layout().addWidget(self.tab_widget)
        
        return main_widget
    def create_inventory_tab(self):
        inventory_widget = QWidget()
        layout = QVBoxLayout()
        inventory_widget.setLayout(layout)
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(9)
        self.inventory_table.setHorizontalHeaderLabels(
            ["Item ID", "Market ID", "Quantity", "Title", "Set Name", "Release", "Rarity", "Price", "Notes"]
        )
        self.inventory_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.inventory_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.inventory_table)
        delete_button = QPushButton("Delete Selected Record")
        delete_button.clicked.connect(self.delete_selected_record)
        layout.addWidget(delete_button)
        self.update_inventory_table()
        return inventory_widget
     
    def keyPressEvent(self, event):
        # Press the F1 key to clear and navigate to the search bar
        key = event.key()
        if key == Qt.Key.Key_F1:
            self.search_bar.clear()
            self.search_bar.setFocus()
            event.accept()
        # Press the F2 to navigate to the search results
        if key == Qt.Key.Key_F2:
            self.results_list.setFocus()
            event.accept()
        else:
            super().keyPressEvent(event) # Pass the event to the base class for other keys
            
    def search_database(self):
        query = self.search_bar.text()
        self.cursor.execute("SELECT join_id, name, set_name, set_release, rarity, index_market FROM products WHERE name LIKE ?", ('%' + query + '%',))
        results = self.cursor.fetchall()
        print(f"Search query {query} has {len(results)} results")
        
        self.results_list.clear()
        for item_id, title, set_name, set_release, rarity, index_market in results:
            # Format for the search results
            card_id = item_id[:-len(rarity.split(' ')[0])]
            self.results_list.addItem(f"{title} ({card_id})({' '.join(rarity.split(' ')[1:])} from {set_name} on {set_release})[{index_market}]")
    
    def get_card(self, id):
        join_id = 'index_market'
        self.cursor.execute(f"SELECT join_id, name, set_name, rarity, set_release, price, index_market FROM products WHERE {join_id} == ?", (id,))
        results = self.cursor.fetchall()[0]
        return results
    
    def parse_id(self, item, tag_char = "["):
        tag = item.text().split(tag_char, 1)[1]
        result = tag[:-len(tag_char)]
        print(f"Parsed id: {result}")
        return result
    
    def on_item_clicked(self, item):
        results = self.get_card(self.parse_id(item))
        self.load_image(results[6])  # Load card image when item is selected
        print(f"Selected item: {item.text()}")

    def update_inventory(self):
        selected_item = self.results_list.currentItem()
        if selected_item:
            results = self.get_card(self.parse_id(selected_item))
            # check if there's notes
            if not self.notes_edit.toPlainText():
                no_notes_error = QMessageBox()
                no_notes_error.setText("Notes are required. Please enter Unlimited if there is nothing noteworthy.")
                no_notes_error.exec()
                return

            self.inventory.append({
                'Item ID': results[0],
                'Market ID': results[6],
                'Quantity': self.quantity_spinbox.value(),
                'Title': results[1],
                'Set Name': results[2],
                'Release': results[4],
                'Rarity': results[3],
                'Price': results[5],
                'Notes': self.notes_edit.toPlainText()
            })
            self.update_inventory_table()

    def update_inventory_table(self):
        self.inventory_table.setRowCount(0)
        for item in self.inventory:
            row_position = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row_position)
            for column, key in enumerate(item.keys()):
                self.inventory_table.setItem(row_position, column, QTableWidgetItem(str(item[key])))
    
    def save_to_spreadsheet(self):
        if len(self.inventory) < 1:
            return
        if os.path.exists(self.default_filename):
            try:
                df = pd.read_excel(self.default_filename, engine='openpyxl')
                new_row = pd.DataFrame(self.inventory)
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_excel(self.default_filename, index=False, engine='openpyxl')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to append to the spreadsheet: {e}")
        else:
            pd.DataFrame(self.inventory).to_excel(self.default_filename, index=False)
        
        print(f"Data saved to {self.default_filename}")
        self.inventory = []
        self.update_inventory_table()
        print("Inventory cleared")
    
    def update_spreadsheet_prices(self):
        def get_price(row):
            id = row['Item ID']
            return self.get_card(id)[5]

        try:
            # Create and configure the progress dialog
            progress_dialog = QProgressDialog("Updating prices...", "Cancel", 0, 100, self)
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.show()

            # Load the spreadsheet data
            df = pd.read_excel(self.default_filename, engine='openpyxl')
            total_rows = len(df)

            # Update prices with progress dialog updates
            for index, row in df.iterrows():
                if progress_dialog.wasCanceled():
                    QMessageBox.critical(self, "Cancelled", "Price update was cancelled by the user.")
                    return

                df.at[index, 'Price'] = get_price(row)
                progress_dialog.setValue(int((index + 1) / total_rows * 100))

            # Save the updated prices back to the spreadsheet
            df.to_excel(self.default_filename, index=False, engine='openpyxl')

            QMessageBox.information(self, "Success", "Prices have been updated successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update prices to the spreadsheet: {e}\n{traceback.format_exc()}")
        
    def delete_selected_record(self):
        selected_row = self.inventory_table.currentRow()
        if selected_row is None:
            QMessageBox.warning(self, "Warning", "No record selected for deletion.")
            return
        del self.inventory[selected_row]
        self.update_inventory_table()
    
    def load_image(self, product_id):
        image_url = f"https://tcgplayer-cdn.tcgplayer.com/product/{product_id}_in_600x600.jpg"
        print(f"Loading {product_id} with {image_url}")
        self.image_request = QNetworkRequest(QUrl(image_url))
        self.network_manager.get(self.image_request)

    def on_image_loaded(self, reply: QNetworkReply):
        print("Completed image load.")
        if (reply.error() == reply.NetworkError.NoError):
            image_data = reply.readAll()
            image = QImage()
            if image.loadFromData(image_data, "JPEG"):
                pixmap = QPixmap.fromImage(image)
                self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.image_label.setText("Invalid image format.")
        else:
            # warning: recursive
            # todo: placeholder image in the database
            self.load_image('23009') # black hole
    
    def on_selection_changed(self, current_row):
        """Slot to update the image whenever the selected row changes."""
        if current_row >= 0:
            selected_item = self.results_list.item(current_row)
            if selected_item:
                self.on_item_clicked(selected_item)
    
    def closeEvent(self, event):
        print("Closing application")
        """Override close event to perform cleanup."""
        self.conn.close()  # Close the database connection
        event.accept()  # Accept the event to close the window

def main():
    app = QApplication(sys.argv)
    window = YGOInventoryApp()
    window.show()

    # Handle termination signals
    def on_exit_signal():
        app.quit()

    signal.signal(signal.SIGINT, lambda signum, frame: on_exit_signal())
    signal.signal(signal.SIGTERM, lambda signum, frame: on_exit_signal())

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
