from __future__ import annotations

from nicegui import ui
import httpx


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


def _header_nav(active: str) -> None:
    with ui.header().classes('items-center justify-between'):
        ui.label('Trading Middleware').classes('text-lg')
        with ui.row().classes('items-center'):
            ui.link('Dashboard', '/').classes('text-primary' if active == 'dashboard' else '')
            ui.link('Positions', '/positions').classes('text-primary' if active == 'positions' else '')
            ui.link('Orders', '/orders').classes('text-primary' if active == 'orders' else '')
            ui.link('Risk', '/risk').classes('text-primary' if active == 'risk' else '')
            ui.link('Metrics', '/metrics', new_tab=True)


@ui.page('/')
async def dashboard_page() -> None:
    _header_nav('dashboard')
    with ui.row().classes('w-full'):
        with ui.card().classes('w-full'):
            ui.label('Quick Glance').classes('text-md font-bold')
            total_positions = ui.label('Positions: ...')
            margin_label = ui.label('Available Margin: ...')

            async def refresh_glance():
                try:
                    positions = await fetch_json('/positions')
                    total_positions.text = f"Positions: {len(positions)}"
                except Exception:
                    total_positions.text = 'Positions: error'
                try:
                    margin = await fetch_json('/positions/margin')
                    margin_label.text = f"Available Margin: {margin.get('available', 'NA')}"
                except Exception:
                    margin_label.text = 'Available Margin: error'

            ui.timer(2.0, refresh_glance)


@ui.page('/positions')
async def positions_page() -> None:
    _header_nav('positions')
    ui.label('Positions').classes('text-md font-bold')
    table = ui.table(columns=[
        {'name': 'tradingSymbol', 'label': 'Symbol', 'field': 'tradingSymbol'},
        {'name': 'exchangeSegment', 'label': 'Exchange', 'field': 'exchangeSegment'},
        {'name': 'productType', 'label': 'Product', 'field': 'productType'},
        {'name': 'netQty', 'label': 'Net Qty', 'field': 'netQty'},
        {'name': 'buyAvg', 'label': 'Buy Avg', 'field': 'buyAvg'},
        {'name': 'unrealizedProfit', 'label': 'P&L', 'field': 'unrealizedProfit'},
    ], rows=[]).classes('w-full')

    async def load_positions():
        try:
            rows = await fetch_json('/positions')
            table.rows = rows
            table.update()
        except Exception:
            pass

    with ui.row():
        ui.button('Refresh', on_click=load_positions)
    ui.timer(2.0, load_positions)


@ui.page('/orders')
async def orders_page() -> None:
    _header_nav('orders')
    ui.label('Order Book').classes('text-md font-bold')
    table = ui.table(columns=[
        {'name': 'orderId', 'label': 'Order ID', 'field': 'orderId'},
        {'name': 'tradingSymbol', 'label': 'Symbol', 'field': 'tradingSymbol'},
        {'name': 'transactionType', 'label': 'Side', 'field': 'transactionType'},
        {'name': 'orderStatus', 'label': 'Status', 'field': 'orderStatus'},
        {'name': 'quantity', 'label': 'Qty', 'field': 'quantity'},
        {'name': 'price', 'label': 'Price', 'field': 'price'},
        {'name': 'time', 'label': 'Time', 'field': 'time'},
    ], rows=[]).classes('w-full')

    async def load_orders():
        try:
            rows = await fetch_json('/orders')
            table.rows = rows
            table.update()
        except Exception:
            pass

    with ui.row():
        ui.button('Refresh', on_click=load_orders)
        async def cancel_all():
            try:
                await post_json('/orders/cancel_all', {})
                await load_orders()
            except Exception:
                pass
        ui.button('Cancel All', on_click=cancel_all, color='red')
    ui.timer(2.0, load_orders)


@ui.page('/risk')
async def risk_page() -> None:
    _header_nav('risk')
    with ui.row().classes('w-full'):
        with ui.card().classes('w-full'):
            ui.label('Risk Settings').classes('text-md font-bold')
            settings_area = ui.column()

            async def load_settings():
                data = await fetch_json('/risk/settings')
                settings_area.clear()
                ui.label(f"Locked: {data.get('risk_locked')}")
                ui.label(f"Lock until: {data.get('risk_lock_until')}")
                ui.label(f"Max daily total loss: {data.get('max_daily_total_loss')}")
                ui.label(f"Max daily loss per position: {data.get('max_daily_loss_per_position')}")
                ui.label(f"Per position profit target: {data.get('per_position_daily_profit_target')}")
                ui.label(f"Max daily total profit target: {data.get('max_daily_total_profit_target')}")

            async def lock():
                await post_json('/risk/lock', {})
                await load_settings()

            async def unlock():
                await post_json('/risk/unlock', {})
                await load_settings()

            with ui.row():
                ui.button('Lock Risk (until next day 5 PM)', on_click=lock, color='red')
                ui.button('Unlock (if expired)', on_click=unlock, color='green')

        with ui.card().classes('w-full'):
            ui.label('Kill Switch').classes('text-md font-bold')
            status_label = ui.label('Status: ...')

            async def refresh_status():
                data = await fetch_json('/kill/status')
                status_label.text = f"Status: {'ACTIVE' if data.get('is_active') else 'INACTIVE'} ({data.get('reason')})"

            async def activate():
                await post_json('/kill/activate', {"reason": "manual"})
                await refresh_status()

            async def deactivate():
                await post_json('/kill/deactivate', {"reason": "manual_reset_after_hours"})
                await refresh_status()

            with ui.row():
                ui.button('Activate Kill Switch', on_click=activate, color='red')
                ui.button('Deactivate', on_click=deactivate, color='green')

    ui.timer(2.0, refresh_status)
    ui.timer(5.0, load_settings)


# Keep compatibility with main.py which calls create_ui()
# It is safe to no-op as pages are registered above via decorators.

def create_ui() -> None:
    pass
