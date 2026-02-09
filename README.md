# ERP / PDV Desktop em Python

Sistema **ERP / PDV desktop** desenvolvido em **Python**, com foco em controle de produtos, estoque, vendas (caixa), relatórios e dashboard gerencial.

Projeto criado com objetivo de **estudo prático, portfólio e evolução para um sistema comercial real**.

---

## 🧱 Stack Tecnológica

- **Python 3.11+**
- **PySide6 (Qt)** – Interface desktop
- **FastAPI** – API local
- **SQLAlchemy (async)** – ORM
- **SQLite** (modo local/offline)
- **PostgreSQL** (planejado para multi-PC)
- **Alembic** – Migrations de banco
- Arquitetura **offline-first**

---

## 🚀 Funcionalidades Implementadas

### 📦 Produtos
- Cadastro, edição e exclusão
- SKU opcional
- Controle de estoque em tempo real

### 📊 Estoque
- Ajustes manuais (entrada/saída)
- Histórico de movimentações
- Integração automática com vendas

### 🧾 PDV / Caixa
- Busca rápida por nome ou SKU
- Adição ao carrinho via **Enter**
- Controle de quantidade
- Finalização de venda
- Atualização automática do estoque

### 📈 Dashboard
- Total de produtos
- Estoque total
- Produtos com estoque baixo
- Gráfico de movimentação de estoque (últimos dias)

### 📑 Relatórios
- Resumo geral
- Movimentações por período
- Base para relatórios financeiros

### 🏭 Fornecedores
- Cadastro e listagem
- Estrutura pronta para vínculo com produtos

---

## 🖥️ Screenshots

## 🖥️ Screenshots

![Dashboard](docs/screenshots/dashboard.png)
![Produtos](docs/screenshots/products.png)
![PDV](docs/screenshots/pos.png)
![Relatórios](docs/screenshots/reports.png)





⚙️ Como rodar o projeto (Windows)

1️⃣ Criar ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

2️⃣ Instalar dependências
pip install -U pip
pip install -e .

3️⃣ Configurar ambiente
copy .env.example .env

4️⃣ Rodar aplicação (UI + API)
python -m app.main

🛠️ Banco de dados & Migrations
alembic upgrade head



🗺️ Roadmap (Próximos Passos)

💰 Preço de venda e custo por produto

📉 Relatório de lucro e faturamento

💳 Métodos de pagamento (dinheiro, PIX, cartão)

🧾 Integração com NF-e (estudo)

👤 Usuários e permissões

🌐 Modo multi-PC (PostgreSQL)

🎨 Interface com ícones e tema moderno

📌 Observações
Este projeto não contém dados reais, senhas ou informações sensíveis.
Ideal para estudos, testes e evolução contínua.

👨‍💻 Autor
Kevin Bertolini
Projeto desenvolvido como parte da transição e evolução profissional na área de tecnologia.