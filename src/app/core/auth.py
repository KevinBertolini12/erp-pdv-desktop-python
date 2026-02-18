class UserSession:
    """Gerenciador central de quem está no comando do ERP"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSession, cls).__new__(cls)
            cls._instance.user_id = None
            cls._instance.user_name = "Visitante"
            cls._instance.role = "vendedor" # vendedor, gerente, admin
            cls._instance.business_type = "workshop"
        return cls._instance

    def start(self, name, role, b_type):
        self.user_name = name
        self.role = role
        self.business_type = b_type

    def has_permission(self, level_required):
        # Hierarquia: admin > gerente > vendedor
        levels = {"vendedor": 1, "gerente": 2, "admin": 3}
        return levels.get(self.role, 0) >= levels.get(level_required, 0)

# Instância global para ser usada em qualquer página
current_session = UserSession()