from __future__ import annotations

from nicegui import ui
import httpx
import asyncio

API_BASE = "http://localhost:8000/api"

async def fetch_json(path: str):
    async with httpx.AsyncClient(base_url=API_BASE, timeout=5.0) as client:
        r = await client.get(path)
        r.raise_for_status()
        return r.json()

async def post_json(path: str, payload: dict):
    async with httpx.AsyncClient(base_url=API_BASE, timeout=5.0) as client:
        r = await client.post(path, json=payload)
        r.raise_for_status()
        return r.json()

def _header_nav(active: str, user: str = "Trader") -> None:
    with ui.header().classes('items-center justify-between bg-blue-600 text-white p-4'):
        ui.label('🚀 SimpleApp Trading Middleware').classes('text-xl font-bold')
        with ui.row().classes('items-center gap-4'):
            ui.link('📊 Dashboard', '/').classes('text-white hover:text-blue-200' if active == 'dashboard' else 'text-blue-200')
            ui.link('⚙️ Settings', '/settings').classes('text-white hover:text-blue-200' if active == 'settings' else 'text-blue-200')
            ui.link('⚠️ Risk', '/risk').classes('text-white hover:text-blue-200' if active == 'risk' else 'text-blue-200')
            ui.link('📈 Trading', '/trading').classes('text-white hover:text-blue-200' if active == 'trading' else 'text-blue-200')
            ui.link('💼 Positions', '/positions').classes('text-white hover:text-blue-200' if active == 'positions' else 'text-blue-200')
            ui.link('📋 Orders', '/orders').classes('text-white hover:text-blue-200' if active == 'orders' else 'text-blue-200')
            ui.link('🏦 Holdings', '/holdings').classes('text-white hover:text-blue-200' if active == 'holdings' else 'text-blue-200')
            ui.label(f'👤 {user}').classes('text-sm text-blue-200')

@ui.page('/trading')
async def trading_page() -> None:
    _header_nav('trading')
    
    ui.add_head_html('<title>Trading - SimpleApp Trading</title>')
    
    # Create UI elements as class variables so they can be accessed by functions
    class TradingUI:
        def __init__(self):
            self.symbol_input = None
            self.ltp_label = None
            self.orders_container = None
    
    trading_ui = TradingUI()
    
    with ui.column().classes('w-full p-6 bg-gray-50'):
        # Page Title
        ui.label('📈 Trading Dashboard').classes('text-3xl font-bold text-gray-800 mb-6')
        
        # Symbol Search and Quote Section
        with ui.card().classes('w-full mb-6'):
            ui.label('🔍 Symbol Search & Quote').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.grid(columns=3).classes('w-full gap-4 items-end'):
                ui.label('Trading Symbol:').classes('text-sm font-medium text-gray-600')
                trading_ui.symbol_input = ui.input('Enter symbol (e.g., RELIANCE)').classes('w-full')
                ui.button('🔍 Search', on_click=lambda: search_symbol(trading_ui)).classes('bg-blue-500 text-white px-4 py-2')
            
            with ui.row().classes('w-full justify-center mt-4'):
                trading_ui.ltp_label = ui.label('Last Traded Price: ₹0.00').classes('text-2xl font-bold text-blue-600')
            
            with ui.row().classes('w-full justify-center mt-2'):
                ui.button('📊 Get Quote', on_click=lambda: get_quote(trading_ui)).classes('bg-green-500 text-white px-6 py-2')
        
        # Order Placement Section
        with ui.card().classes('w-full mb-6'):
            ui.label('📝 Place Order').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.grid(columns=2).classes('w-full gap-6'):
                # Left Column - Order Details
                with ui.column().classes('gap-4'):
                    ui.label('Order Type:').classes('text-sm font-medium text-gray-600')
                    order_type = ui.select(['MARKET', 'LIMIT'], value='MARKET').classes('w-full')
                    
                    ui.label('Transaction Type:').classes('text-sm font-medium text-gray-600')
                    transaction_type = ui.select(['BUY', 'SELL'], value='BUY').classes('w-full')
                    
                    ui.label('Quantity:').classes('text-sm font-medium text-gray-600')
                    quantity = ui.number('1', min=1, step=1).props('outlined dense').classes('w-full')
                    
                    ui.label('Price (₹):').classes('text-sm font-medium text-gray-600')
                    price = ui.number('0.00', min=0.01, step=0.01).props('outlined dense').classes('w-full')
                
                # Right Column - Order Summary
                with ui.column().classes('gap-4'):
                    ui.label('Order Summary:').classes('text-sm font-medium text-gray-600')
                    
                    with ui.card().classes('w-full p-4 bg-blue-50'):
                        ui.label('Symbol: Not selected').classes('text-sm text-gray-600')
                        ui.label('Type: MARKET').classes('text-sm text-gray-600')
                        ui.label('Side: BUY').classes('text-sm text-gray-600')
                        ui.label('Quantity: 1').classes('text-sm text-gray-600')
                        ui.label('Price: Market').classes('text-sm text-gray-600')
                    
                    ui.button('🚀 Place Order', on_click=lambda: place_order(trading_ui, order_type, transaction_type, quantity, price)).classes('bg-green-500 text-white px-6 py-2 w-full')
        
        # Recent Orders Section
        with ui.card().classes('w-full mb-6'):
            ui.label('📋 Recent Orders').classes('text-xl font-bold text-gray-700 mb-4')
            
            trading_ui.orders_container = ui.table(columns=[
                {'name': 'orderId', 'label': 'Order ID', 'field': 'orderId'},
                {'name': 'tradingSymbol', 'label': 'Symbol', 'field': 'tradingSymbol'},
                {'name': 'transactionType', 'label': 'Side', 'field': 'transactionType'},
                {'name': 'orderStatus', 'label': 'Status', 'field': 'orderStatus'},
                {'name': 'quantity', 'label': 'Qty', 'field': 'quantity'},
                {'name': 'price', 'label': 'Price', 'field': 'price'},
                {'name': 'time', 'label': 'Time', 'field': 'time'}
            ], rows=[]).classes('w-full')
            
            with ui.row().classes('w-full justify-center mt-4'):
                ui.button('🔄 Refresh Orders', on_click=lambda: load_recent_orders(trading_ui)).classes('bg-blue-500 text-white px-4 py-2')
        
        # Navigation Links
        with ui.row().classes('w-full justify-center gap-4 mt-6'):
            ui.button('📊 Dashboard', on_click=lambda: ui.navigate.to('/')).classes('bg-blue-500 text-white px-4 py-2')
            ui.button('⚠️ Risk', on_click=lambda: ui.navigate.to('/risk')).classes('bg-red-500 text-white px-4 py-2')
            ui.button('⚙️ Settings', on_click=lambda: ui.navigate.to('/settings')).classes('bg-purple-500 text-white px-4 py-2')
            ui.button('💼 Positions', on_click=lambda: ui.navigate.to('/positions')).classes('bg-green-500 text-white px-4 py-2')
            ui.button('📋 Orders', on_click=lambda: ui.navigate.to('/orders')).classes('bg-indigo-500 text-white px-4 py-2')
    
    # Load initial data
    await load_recent_orders(trading_ui)
    
    # Set up auto-refresh timer
    ui.timer(10.0, lambda: asyncio.create_task(load_recent_orders(trading_ui)))

async def search_symbol(trading_ui):
    """Search for a trading symbol"""
    try:
        symbol = trading_ui.symbol_input.value.strip().upper()
        if not symbol:
            ui.notify('❌ Please enter a symbol to search', type='negative')
            return
        
        ui.notify(f'🔍 Searching for symbol: {symbol}', type='info')
        
        # In a real implementation, this would search the master contract
        # For now, we'll simulate a search
        await asyncio.sleep(1)
        
        if symbol in ['RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICIBANK']:
            ui.notify(f'✅ Symbol {symbol} found!', type='positive')
            trading_ui.symbol_input.value = symbol
        else:
            ui.notify(f'❌ Symbol {symbol} not found', type='negative')
            
    except Exception as e:
        ui.notify(f'❌ Error searching symbol: {str(e)}', type='negative')

async def get_quote(trading_ui):
    """Get quote for the selected symbol"""
    try:
        symbol = trading_ui.symbol_input.value.strip().upper()
        if not symbol:
            ui.notify('❌ Please enter a symbol first', type='negative')
            return
        
        ui.notify(f'📊 Getting quote for {symbol}...', type='info')
        
        # In a real implementation, this would call the market data API
        # For now, we'll simulate a quote
        await asyncio.sleep(1)
        
        # Simulate different prices for different symbols
        mock_prices = {
            'RELIANCE': 2450.50,
            'TCS': 3850.75,
            'INFY': 1450.25,
            'HDFC': 1650.00,
            'ICICIBANK': 950.50
        }
        
        if symbol in mock_prices:
            price = mock_prices[symbol]
            trading_ui.ltp_label.text = f'Last Traded Price: ₹{price:.2f}'
            ui.notify(f'✅ Quote received for {symbol}: ₹{price:.2f}', type='positive')
        else:
            trading_ui.ltp_label.text = 'Last Traded Price: ₹0.00'
            ui.notify(f'❌ No quote available for {symbol}', type='negative')
            
    except Exception as e:
        ui.notify(f'❌ Error getting quote: {str(e)}', type='negative')

async def place_order(trading_ui, order_type, transaction_type, quantity, price):
    """Place a trading order"""
    try:
        symbol = trading_ui.symbol_input.value.strip().upper()
        if not symbol:
            ui.notify('❌ Please enter a symbol first', type='negative')
            return
        
        # Validate order parameters
        if quantity.value <= 0:
            ui.notify('❌ Quantity must be greater than 0', type='negative')
            return
        
        if order_type.value == 'LIMIT' and price.value <= 0:
            ui.notify('❌ Price must be greater than 0 for limit orders', type='negative')
            return
        
        # Prepare order data
        order_data = {
            'tradingSymbol': symbol,
            'transactionType': transaction_type.value,
            'orderType': order_type.value,
            'quantity': int(quantity.value),
            'price': float(price.value) if order_type.value == 'LIMIT' else 0,
            'productType': 'INTRADAY',
            'exchangeSegment': 'NSE'
        }
        
        ui.notify(f'🚀 Placing {transaction_type.value} order for {symbol}...', type='info')
        
        # In a real implementation, this would call the order placement API
        # For now, we'll simulate order placement
        await asyncio.sleep(2)
        
        # Simulate successful order placement
        order_id = f"ORD{len(trading_ui.orders_container.rows) + 1:06d}"
        
        ui.notify(f'✅ Order placed successfully! Order ID: {order_id}', type='positive')
        
        # Refresh orders list
        await load_recent_orders(trading_ui)
        
        # Clear form
        trading_ui.symbol_input.value = ''
        trading_ui.ltp_label.text = 'Last Traded Price: ₹0.00'
        quantity.value = 1
        price.value = 0.00
        
    except Exception as e:
        ui.notify(f'❌ Error placing order: {str(e)}', type='negative')

async def load_recent_orders(trading_ui):
    """Load recent orders from backend"""
    try:
        # Get orders from backend
        orders = await fetch_json('/orders')
        
        # Update orders table
        trading_ui.orders_container.rows = orders
        trading_ui.orders_container.update()
        
    except Exception as e:
        ui.notify(f'❌ Error loading orders: {str(e)}', type='negative')

# Export the trading page function
__all__ = ['trading_page']
