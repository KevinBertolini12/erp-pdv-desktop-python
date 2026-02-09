import httpx


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    # -------- health --------
    def health(self) -> dict:
        r = httpx.get(f"{self.base_url}/health", timeout=2.0)
        r.raise_for_status()
        return r.json()

    # -------- products --------
    def list_products(self) -> list[dict]:
        r = httpx.get(f"{self.base_url}/products", timeout=5.0)
        r.raise_for_status()
        return r.json()

    def create_product(self, name: str, sku: str | None = None) -> dict:
        r = httpx.post(f"{self.base_url}/products", json={"name": name, "sku": sku}, timeout=10.0)
        r.raise_for_status()
        return r.json()

    def update_product(self, product_id: int, name: str, sku: str | None = None) -> dict:
        r = httpx.put(f"{self.base_url}/products/{product_id}", json={"name": name, "sku": sku}, timeout=10.0)
        r.raise_for_status()
        return r.json()

    def delete_product(self, product_id: int) -> None:
        r = httpx.delete(f"{self.base_url}/products/{product_id}", timeout=10.0)
        r.raise_for_status()

    def adjust_stock(self, product_id: int, delta: int, reason: str) -> dict:
        r = httpx.post(
            f"{self.base_url}/products/{product_id}/stock",
            json={"delta": int(delta), "reason": reason},
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json()

    # -------- reports --------
    def reports_summary(self) -> dict:
        r = httpx.get(f"{self.base_url}/reports/summary", timeout=10.0)
        r.raise_for_status()
        return r.json()

    def reports_stock_moves_7d(self) -> dict:
        r = httpx.get(f"{self.base_url}/reports/stock_moves_7d", timeout=10.0)
        r.raise_for_status()
        return r.json()

    def reports_stock_moves_range(self, start: str, end: str) -> dict:
        r = httpx.get(f"{self.base_url}/reports/stock_moves_range", params={"start": start, "end": end}, timeout=10.0)
        r.raise_for_status()
        return r.json()

    # -------- sales --------
    def create_sale(self, items: list[dict]) -> dict:
        r = httpx.post(f"{self.base_url}/sales", json={"items": items}, timeout=10.0)
        r.raise_for_status()
        return r.json()
    

    def list_suppliers(self) -> list[dict]:
        r = httpx.get(f"{self.base_url}/suppliers", timeout=10.0)
        r.raise_for_status()
        return r.json()

    def create_supplier(self, name: str, document: str | None = None, phone: str | None = None, email: str | None = None) -> dict:
        r = httpx.post(
            f"{self.base_url}/suppliers",
            json={"name": name, "document": document, "phone": phone, "email": email},
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json()

    def update_supplier(self, supplier_id: int, name: str | None = None, document: str | None = None, phone: str | None = None, email: str | None = None) -> dict:
        r = httpx.put(
            f"{self.base_url}/suppliers/{supplier_id}",
            json={"name": name, "document": document, "phone": phone, "email": email},
            timeout=10.0,
        )
        r.raise_for_status()
        return r.json()

    def delete_supplier(self, supplier_id: int) -> dict:
        r = httpx.delete(f"{self.base_url}/suppliers/{supplier_id}", timeout=10.0)
        r.raise_for_status()
        return r.json()



    