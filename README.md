# yugioh-ccd
A Yu-Gi-Oh! TCG complete database with reproducible scripts for refreshing data primarily hosted on Kaggle

<a href="https://www.kaggle.com/datasets/hammadus/yugioh-full-card-database-index-august-1st-2025" target="_blank">Click here to view data on Kaggle</a>

# Yu-Gi-Oh! Complete Card Database

This dataset provides a comprehensive and detailed collection of Yu-Gi-Oh! trading cards, compiled from multiple sources including Konami’s official website. It features data on every Yu-Gi-Oh! card ever released, making it an invaluable resource for enthusiasts, researchers, and developers interested in the game.

## Key Features
    
- Card Details: Includes unique identifiers, card names, types (Monster, Spell, Trap, etc.), and detailed descriptions.
- Attributes: Comprehensive information on card attributes such as level/rank, attack/defense points, and attributes for monsters.
- Set Information: Data on all sets each card appears in, including set names, codes, and rarities.
- Release Dates: When each card was released.
- Market Data: Average market prices where available from TCGPlayer

## Data Structure

The data are contained in CSV files that can be opened in your choice of spreadsheet software. To view a preview, scroll to the Data Explorer and make sure to select all columns from the drop down arrow. Below are general descriptions of the main database, for more detailed information about each column, view the Data Explorer.

- 'name', 'description', 'type', 'sub_type', 'attribute', 'rank', 'attack', 'defense'
    - These fields describe the game related fields from Konami
- 'rarity', 'set_name', 'set_id', 'set_release',
    - The in-person card details and availability
-  'market_name', 'price', 'price_asof', 'price_change', 'avg_sale_days',
    - The collectables market and price details pulled from TCGPlayer
- 'index', 'index_market', 'join_id'
    - Database identifiers related to programming the scripts

## Usage

This dataset can be used for a variety of purposes, including:

- Card Analysis: Explore the distribution of card types, attributes, and rarities.
- Market Research: Analyze trends in card prices over time.
- Game Development: Integrate card data into Yu-Gi-Oh! related applications or tools.
- Research: Conduct studies on the game’s evolution and card design.
