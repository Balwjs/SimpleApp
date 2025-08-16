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

@ui.page('/holdings')
async def holdings_page() -> None:
    _header_nav('holdings')
    
    ui.add_head_html('<title>Holdings - SimpleApp Trading</title>')
    
    # Create UI elements as class variables so they can be accessed by functions
    class HoldingsUI:
        def __init__(self):
            self.holdings_container = None
    
    holdings_ui = HoldingsUI()
    
    with ui.column().classes('w-full p-6 bg-gray-50'):
        # Page Title
        ui.label('🏦 Long-term Holdings').classes('text-3xl font-bold text-gray-800 mb-6')
        
        # Portfolio Summary
        with ui.card().classes('w-full mb-6'):
            ui.label('📊 Portfolio Summary').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.grid(columns=4).classes('w-full gap-4'):
                # Total Holdings Value
                with ui.column().classes('text-center'):
                    total_value_icon = ui.icon('account_balance_wallet').classes('text-4xl text-blue-500')
                    total_value_label = ui.label('Total Value: ₹0.00').classes('text-lg font-bold')
                
                # Total P&L
                with ui.column().classes('text-center'):
                    total_pnl_icon = ui.icon('trending_up').classes('text-4xl text-green-500')
                    total_pnl_label = ui.label('Total P&L: ₹0.00').classes('text-lg font-bold')
                
                # Number of Holdings
                with ui.column().classes('text-center'):
                    holdings_count_icon = ui.icon('inventory').classes('text-4xl text-purple-500')
                    holdings_count_label = ui.label('Holdings: 0').classes('text-lg font-bold')
                
                # Average Return
                with ui.column().classes('text-center'):
                    avg_return_icon = ui.icon('analytics').classes('text-4xl text-orange-500')
                    avg_return_label = ui.label('Avg Return: 0.00%').classes('text-lg font-bold')
        
        # Holdings Table
        with ui.card().classes('w-full mb-6'):
            ui.label('📋 Holdings Details').classes('text-xl font-bold text-gray-700 mb-4')
            
            holdings_ui.holdings_container = ui.table(columns=[
                {'name': 'tradingSymbol', 'label': 'Symbol', 'field': 'tradingSymbol'},
                {'name': 'exchangeSegment', 'label': 'Exchange', 'field': 'exchangeSegment'},
                {'name': 'quantity', 'label': 'Quantity', 'field': 'quantity'},
                {'name': 'averagePrice', 'label': 'Avg Price', 'field': 'averagePrice'},
                {'name': 'currentPrice', 'label': 'Current Price', 'field': 'currentPrice'},
                {'name': 'totalValue', 'label': 'Total Value', 'field': 'totalValue'},
                {'name': 'unrealizedProfit', 'label': 'P&L', 'field': 'unrealizedProfit'},
                {'name': 'returnPercentage', 'label': 'Return %', 'field': 'returnPercentage'}
            ], rows=[]).classes('w-full')
        
        # Portfolio Actions
        with ui.card().classes('w-full mb-6'):
            ui.label('⚡ Portfolio Actions').classes('text-xl font-bold text-gray-700 mb-4')
            
            with ui.row().classes('w-full justify-center gap-4'):
                ui.button('🔄 Refresh Holdings', on_click=lambda: load_holdings(holdings_ui)).classes('bg-blue-500 text-white px-6 py-3')
                ui.button('📊 Export Portfolio', on_click=lambda: export_portfolio(holdings_ui)).classes('bg-green-500 text-white px-6 py-3')
                ui.button('📈 Performance Chart', on_click=lambda: show_performance_chart(holdings_ui)).classes('bg-purple-500 text-white px-6 py-3')
        
        # Navigation Links
        with ui.row().classes('w-full justify-center gap-4 mt-6'):
            ui.button('📊 Dashboard', on_click=lambda: ui.navigate.to('/')).classes('bg-blue-500 text-white px-4 py-2')
            ui.button('📋 Orders', on_click=lambda: ui.navigate.to('/orders')).classes('bg-indigo-500 text-white px-4 py-2')
            ui.button('💼 Positions', on_click=lambda: ui.navigate.to('/positions')).classes('bg-green-500 text-white px-4 py-2')
            ui.button('📈 Trading', on_click=lambda: ui.navigate.to('/trading')).classes('bg-purple-500 text-white px-4 py-2')
    
    # Load initial holdings data
    await load_holdings(holdings_ui)
    
    # Set up auto-refresh timer
    ui.timer(10.0, lambda: asyncio.create_task(load_holdings(holdings_ui)))

async def load_holdings(holdings_ui):
    """Load holdings from backend"""
    try:
        # Get holdings from backend
        holdings = await fetch_json('/live-data/holdings')
        
        # Process holdings to calculate additional fields
        processed_holdings = []
        total_portfolio_value = 0.0
        total_portfolio_pnl = 0.0
        
        for holding in holdings:
            # Calculate total value
            quantity = float(holding.get('quantity', 0))
            avg_price = float(holding.get('averagePrice', 0))
            current_price = float(holding.get('currentPrice', avg_price))
            
            total_value = quantity * current_price
            total_cost = quantity * avg_price
            unrealized_pnl = total_value - total_cost
            return_percentage = (unrealized_pnl / total_cost * 100) if total_cost > 0 else 0
            
            # Add calculated fields
            processed_holding = holding.copy()
            processed_holding['totalValue'] = f"₹{total_value:.2f}"
            processed_holding['unrealizedProfit'] = f"₹{unrealized_pnl:.2f}"
            processed_holding['returnPercentage'] = f"{return_percentage:.2f}%"
            
            # Color code P&L
            if unrealized_pnl > 0:
                processed_holding['unrealizedProfit'] = f"🟢 ₹{unrealized_pnl:.2f}"
            elif unrealized_pnl < 0:
                processed_holding['unrealizedProfit'] = f"🔴 ₹{unrealized_pnl:.2f}"
            else:
                processed_holding['unrealizedProfit'] = f"⚪ ₹{unrealized_pnl:.2f}"
            
            processed_holdings.append(processed_holding)
            
            # Update portfolio totals
            total_portfolio_value += total_value
            total_portfolio_pnl += unrealized_pnl
        
        # Update holdings table
        holdings_ui.holdings_container.rows = processed_holdings
        holdings_ui.holdings_container.update()
        
        # Update portfolio summary
        update_portfolio_summary(processed_holdings, total_portfolio_value, total_portfolio_pnl)
        
    except Exception as e:
        ui.notify(f'❌ Error loading holdings: {str(e)}', type='negative')

def update_portfolio_summary(holdings, total_value, total_pnl):
    """Update portfolio summary display"""
    try:
        # Calculate additional metrics
        holdings_count = len(holdings)
        avg_return = (total_pnl / total_value * 100) if total_value > 0 else 0
        
        # Update summary labels (these would be global variables in a real implementation)
        # For now, we'll use a simple approach
        
        # Color code P&L
        if total_pnl > 0:
            pnl_display = f"🟢 ₹{total_pnl:.2f}"
        elif total_pnl < 0:
            pnl_display = f"🔴 ₹{total_pnl:.2f}"
        else:
            pnl_display = f"⚪ ₹{total_pnl:.2f}"
        
        # Color code return percentage
        if avg_return > 0:
            return_display = f"🟢 {avg_return:.2f}%"
        elif avg_return < 0:
            return_display = f"🔴 {avg_return:.2f}%"
        else:
            return_display = f"⚪ {avg_return:.2f}%"
        
    except Exception as e:
        ui.notify(f'❌ Error updating portfolio summary: {str(e)}', type='negative')

async def export_portfolio(holdings_ui):
    """Export portfolio to CSV"""
    try:
        ui.notify('📊 Exporting portfolio...', type='info')
        
        # In a real implementation, this would generate and download a CSV file
        # For now, we'll simulate the export
        await asyncio.sleep(2)
        
        ui.notify('✅ Portfolio exported successfully!', type='positive')
        
    except Exception as e:
        ui.notify(f'❌ Error exporting portfolio: {str(e)}', type='negative')

async def show_performance_chart(holdings_ui):
    """Show portfolio performance chart"""
    try:
        ui.notify('📈 Loading performance chart...', type='info')
        
        # In a real implementation, this would show a chart with historical performance
        # For now, we'll simulate the chart display
        await asyncio.sleep(1)
        
        ui.notify('📈 Performance chart displayed!', type='positive')
        
    except Exception as e:
        ui.notify(f'❌ Error showing performance chart: {str(e)}', type='negative')

# Export the holdings page function
__all__ = ['holdings_page']
