from odoo import models, api
import logging
import requests

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def action_sync_products(self):
        """
        Sync products by calling external API to update products, stock, and prices.
        This method is triggered by the "Sync Products" button.
        """
        try:
            # Call the sync logic
            self.sync_products()
            # Reload the view after syncing
            return {
                "type": "ir.actions.client",
                "tag": "reload",
            }
        except Exception as e:
            _logger.error(f"Failed to sync products: {e}")
            return

    @api.model
    def sync_products(self):
        """
        Sync products from the external API.
        """
        page = 1
        while True:
            material_data = self._call_external_api("get_material_data", params={"page": page})
            if not material_data or "RETURN" not in material_data or not material_data["RETURN"]["E_DATA"]:
                break
            materials = material_data["RETURN"]["E_DATA"]
            for material in materials:
                product = self.env["product.template"].search([("default_code", "=", material["MATNR"])], limit=1)
                if product:
                    product.write({
                        "name": material["MAKTX"],
                        "default_code": material["MATNR"],
                        "type": "product",
                    })
                else:
                    self.env["product.template"].create({
                        "name": material["MAKTX"],
                        "default_code": material["MATNR"],
                        "type": "product",
                    })
            page += 1
        self._update_stock()
        self._update_prices()

    def _call_external_api(self, endpoint, params=None):
        """
        Helper function to call the external API.
        """
        try:
            BASE_URL = "https://25c8-46-197-53-139.ngrok-free.app"
            HEADERS = {"Content-Type": "application/json"}
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            _logger.error(f"API call failed: {str(e)}")
            return {}

    def _update_stock(self):
        """
        Sync product stock levels from the external API.
        """
        page = 1
        while True:
            stock_data = self._call_external_api("get_material_stock", params={"page": page})
            if not stock_data or "RETURN" not in stock_data or not stock_data["RETURN"]["E_DATA"]:
                break
            for stock in stock_data["RETURN"]["E_DATA"]:
                product = self.env["product.template"].search([("default_code", "=", stock["MATNR"])], limit=1)
                if product:
                    inventory = self.env["stock.inventory"].create({
                        "name": f"Inventory Update for {product.name}",
                        "product_ids": [(6, 0, [product.id])],
                        "line_ids": [(0, 0, {
                            "product_id": product.id,
                            "product_qty": stock["LABST"],
                            "location_id": self.env.ref("stock.stock_location_stock").id,
                        })],
                    })
                    inventory.action_validate()
            page += 1

    def _update_prices(self):
        """
        Sync product prices from the external API.
        """
        page = 1
        while True:
            price_data = self._call_external_api("get_material_price", params={"page": page})
            if not price_data or "RETURN" not in price_data or not price_data["RETURN"]["E_DATA"]:
                break
            for price in price_data["RETURN"]["E_DATA"]:
                product = self.env["product.template"].search([("default_code", "=", price["MATNR"])], limit=1)
                if product:
                    product.list_price = price["KBETR"]
            page += 1

    def call_success_message(self):

        return {
            'effect': {
                'type': 'rainbow_man',
                'message': 'Data Fetched Successfully',
                'fadeout': 'slow'
            }
        }
