import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from app import app, init_database

if __name__ == '__main__':
    # Inicializar banco de dados
    init_database()
    
    # Configurações para produção
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)
