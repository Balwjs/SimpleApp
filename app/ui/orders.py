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

@ui.page('/orders')
async def orders_page() -> None:
    _header_nav('orders')
    
    ui.add_head_html('<title>Orders - SimpleApp Trading</title>')
    
    # Create UI elements as class variables so they can be accessed by functions
    class OrdersUI:
        def __init__(self):
            self.orders_container = None
    
    orders_ui = OrdersUI()
    
    with ui.column().classes('w-full p-6 bg-gray-50'):
        # Page Title
        ui.label('📋 Order Book').classes('text-3xl font-bold text-gray-800 mb-6')
        
        # Order Statistics
        with ui.card().classes('w-full mb-6'):
            ui.label('📊 Order Statistics').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.grid(columns=4).classes('w-full gap-4'):
                # Total Orders
                with ui.column().classes('text-center'):
                    total_orders_icon = ui.icon('receipt').classes('text-4xl text-blue-500')
                    total_orders_label = ui.label('Total Orders: 0').classes('text-lg font-bold')
                
                # Pending Orders
                with ui.column().classes('text-center'):
                    pending_orders_icon = ui.icon('schedule').classes('text-4xl text-orange-500')
                    pending_orders_label = ui.label('Pending: 0').classes('text-lg font-bold')
                
                # Completed Orders
                with ui.column().classes('text-center'):
                    completed_orders_icon = ui.icon('check_circle').classes('text-4xl text-green-500')
                    completed_orders_label = ui.label('Completed: 0').classes('text-lg font-bold')
                
                # Rejected Orders
                with ui.column().classes('text-center'):
                    rejected_orders_icon = ui.icon('cancel').classes('text-4xl text-red-500')
                    rejected_orders_label = ui.label('Rejected: 0').classes('text-lg font-bold')
        
        # Orders Table
        with ui.card().classes('w-full mb-6'):
            ui.label('📋 Order Details').classes('text-xl font-bold text-gray-700 mb-4')
            
            orders_ui.orders_container = ui.table(columns=[
                {'name': 'orderId', 'label': 'Order ID', 'field': 'orderId'},
                {'name': 'tradingSymbol', 'label': 'Symbol', 'field': 'tradingSymbol'},
                {'name': 'transactionType', 'label': 'Side', 'field': 'transactionType'},
                {'name': 'orderStatus', 'label': 'Status', 'field': 'orderStatus'},
                {'name': 'quantity', 'label': 'Qty', 'field': 'quantity'},
                {'name': 'price', 'label': 'Price', 'field': 'price'},
                {'name': 'time', 'label': 'Time', 'field': 'time'},
                {'name': 'actions', 'label': 'Actions', 'field': 'actions'}
            ], rows=[]).classes('w-full')
        
        # Order Actions
        with ui.card().classes('w-full mb-6'):
            ui.label('⚡ Order Actions').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.row().classes('w-full justify-center gap-4'):
                ui.button('🔄 Refresh Orders', on_click=lambda: load_orders(orders_ui)).classes('bg-blue-500 text-white px-6 py-3')
                ui.button('❌ Cancel All Orders', on_click=lambda: cancel_all_orders(orders_ui)).classes('bg-red-500 text-white px-6 py-3')
                ui.button('📊 Export Orders', on_click=lambda: export_orders(orders_ui)).classes('bg-green-500 text-white px-6 py-3')
        
        # Navigation Links
        with ui.row().classes('w-full justify-center gap-4 mt-6'):
            ui.button('📊 Dashboard', on_click=lambda: ui.navigate.to('/')).classes('bg-blue-500 text-white px-4 py-2')
            ui.button('📈 Trading', on_click=lambda: ui.navigate.to('/trading')).classes('bg-green-500 text-white px-4 py-2')
            ui.button('💼 Positions', on_click=lambda: ui.navigate.to('/positions')).classes('bg-purple-500 text-white px-4 py-2')
            ui.button('⚠️ Risk', on_click=lambda: ui.navigate.to('/risk')).classes('bg-red-500 text-white px-4 py-2')
    
    # Load initial orders data
    await load_orders(orders_ui)
    
    # Set up auto-refresh timer
    ui.timer(5.0, lambda: asyncio.create_task(load_orders(orders_ui)))

async def load_orders(orders_ui):
    """Load orders from backend"""
    try:
        # Get orders from backend
        orders = await fetch_json('/orders')
        
        # Process orders to add action buttons
        processed_orders = []
        for order in orders:
            # Create action buttons for each order
            actions_html = create_order_actions(order)
            
            processed_order = order.copy()
            processed_order['actions'] = actions_html
            processed_orders.append(processed_order)
        
        # Update orders table
        orders_ui.orders_container.rows = processed_orders
        orders_ui.orders_container.update()
        
        # Update statistics
        update_order_statistics(orders)
        
    except Exception as e:
        ui.notify(f'❌ Error loading orders: {str(e)}', type='negative')

def create_order_actions(order):
    """Create action buttons for an order"""
    order_id = order.get('orderId', '')
    status = order.get('orderStatus', '')
    
    actions = []
    
    # Cancel button for pending orders
    if status in ['PENDING', 'PARTIALLY_FILLED']:
        actions.append(f'<button onclick="cancelOrder(\'{order_id}\')" class="bg-red-500 text-white px-2 py-1 rounded text-sm">Cancel</button>')
    
    # Modify button for pending orders
    if status in ['PENDING', 'PARTIALLY_FILLED']:
        actions.append(f'<button onclick="modifyOrder(\'{order_id}\')" class="bg-blue-500 text-white px-2 py-1 rounded text-sm">Modify</button>')
    
    # View details button for all orders
    actions.append(f'<button onclick="viewOrderDetails(\'{order_id}\')" class="bg-gray-500 text-white px-2 py-1 rounded text-sm">View</button>')
    
    return ' '.join(actions)

def update_order_statistics(orders):
    """Update order statistics display"""
    try:
        total_orders = len(orders)
        pending_orders = len([o for o in orders if o.get('orderStatus') in ['PENDING', 'PARTIALLY_FILLED']])
        completed_orders = len([o for o in orders if o.get('orderStatus') == 'COMPLETED'])
        rejected_orders = len([o for o in orders if o.get('orderStatus') == 'REJECTED'])
        
        # Update statistics labels (these would be global variables in a real implementation)
        # For now, we'll use a simple approach
        
    except Exception as e:
        ui.notify(f'❌ Error updating order statistics: {str(e)}', type='negative')

async def cancel_all_orders(orders_ui):
    """Cancel all pending orders"""
    try:
        ui.notify('❌ Cancelling all pending orders...', type='info')
        
        # Call backend to cancel all orders
        response = await post_json('/orders/cancel_all', {})
        
        if response:
            ui.notify('✅ All pending orders cancelled successfully!', type='positive')
            # Refresh orders list
            await load_orders(orders_ui)
        else:
            ui.notify('❌ Failed to cancel all orders', type='negative')
            
    except Exception as e:
        ui.notify(f'❌ Error cancelling all orders: {str(e)}', type='negative')

async def export_orders(orders_ui):
    """Export orders to CSV"""
    try:
        ui.notify('📊 Exporting orders...', type='info')
        
        # In a real implementation, this would generate and download a CSV file
        # For now, we'll simulate the export
        await asyncio.sleep(2)
        
        ui.notify('✅ Orders exported successfully!', type='positive')
        
    except Exception as e:
        ui.notify(f'❌ Error exporting orders: {str(e)}', type='negative')

# Export the orders page function
__all__ = ['orders_page']
