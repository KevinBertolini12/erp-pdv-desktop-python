import httpx

class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        # Usando um Client persistente para melhor performance nas requisições
        self.client = httpx.Client(base_url=self.base_url, timeout=10.0)

    def close(self):
        """Fecha a conexão do cliente."""
        self.client.close()

    # -------- health --------
    def health(self) -> dict:
        r = self.client.get("/health", timeout=2.0)
        r.raise_for_status()
        return r.json()

    # -------- products --------
    def list_products(self) -> list[dict]:
        r = self.client.get("/products", timeout=5.0)
        r.raise_for_status()
        return r.json()

    def create_product(self, name: str, sku: str | None = None, price: float = 0.0, 
                       cost_price: float = 0.0, stock_qty: float = 0.0, 
                       min_stock: float = 0.0, product_type: str = "product", 
                       ncm_code: str | None = None, ipi_rate: float = 0.0, 
                       icms_rate: float = 0.0) -> dict:
        """Cria um produto enviando todos os novos campos fiscais e de estoque."""
        data = {
            "name": name,
            "sku": sku,
            "price": price,
            "cost_price": cost_price,
            "stock_qty": stock_qty,
            "min_stock": min_stock,
            "type": product_type,
            "ncm_code": ncm_code,
            "ipi_rate": ipi_rate,
            "icms_rate": icms_rate
        }
        r = self.client.post("/products", json=data)
        r.raise_for_status()
        return r.json()

    def update_product(self, product_id: int, **kwargs) -> dict:
        """
        Atualiza um produto. Aceita argumentos dinâmicos (nome, sku, preco, etc).
        Ex: client.update_product(1, price=50.0, stock_qty=10)
        """
        r = self.client.put(f"/products/{product_id}", json=kwargs)
        r.raise_for_status()
        return r.json()

    def delete_product(self, product_id: int) -> None:
        r = self.client.delete(f"/products/{product_id}")
        r.raise_for_status()

    def adjust_stock(self, product_id: int, delta: int, reason: str) -> dict:
        r = self.client.post(
            f"/products/{product_id}/stock",
            json={"delta": int(delta), "reason": reason}
        )
        r.raise_for_status()
        return r.json()

    # -------- sales --------
    def create_sale(self, items: list[dict]) -> dict:
        r = self.client.post("/sales", json={"items": items})
        r.raise_for_status()
        return r.json()

    def list_sales(self) -> list[dict]:
        """Recupera o histórico de vendas."""
        try:
            r = self.client.get("/sales")
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 405:
                print("⚠️ Erro 405: Rota /sales não aceita GET. Verifique o router no backend.")
            return []

    # -------- reports --------
    def reports_summary(self) -> dict:
        r = self.client.get("/reports/summary")
        r.raise_for_status()
        return r.json()

    def reports_stock_moves_7d(self) -> dict:
        r = self.client.get("/reports/stock_moves_7d")
        r.raise_for_status()
        return r.json()

    def reports_stock_moves_range(self, start: str, end: str) -> dict:
        r = self.client.get("/reports/stock_moves_range", params={"start": start, "end": end})
        r.raise_for_status()
        return r.json()

    # -------- suppliers --------
    def list_suppliers(self) -> list[dict]:
        r = self.client.get("/suppliers")
        r.raise_for_status()
        return r.json()

    def create_supplier(self, name: str, document: str | None = None, 
                        phone: str | None = None, email: str | None = None) -> dict:
        r = self.client.post(
            "/suppliers",
            json={"name": name, "document": document, "phone": phone, "email": email}
        )
        r.raise_for_status()
        return r.json()

    def update_supplier(self, supplier_id: int, **kwargs) -> dict:
        r = self.client.put(f"/suppliers/{supplier_id}", json=kwargs)
        r.raise_for_status()
        return r.json()

    def delete_supplier(self, supplier_id: int) -> dict:
        r = self.client.delete(f"/suppliers/{supplier_id}")
        r.raise_for_status()
        return r.json()