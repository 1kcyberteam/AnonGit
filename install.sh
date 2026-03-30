#!/bin/bash

# Autor: Anonymous
# Versão: 1.1.0

echo "Atualizando pacotes do Termux..."
pkg update && pkg upgrade -y

echo "Instalando dependências (Python e Git)..."
pkg install python git ncurses-utils -y

echo "Configurando a ferramenta personalizada 'mygitui'..."
# No ambiente do usuário, o arquivo git_tui_tool.py deve estar no mesmo diretório
# Se estiver rodando via script, podemos baixar ou copiar o arquivo existente
cp /home/ubuntu/git_tui_tool.py $PREFIX/bin/mygitui
chmod +x $PREFIX/bin/mygitui

echo "
==================================================
  INSTALAÇÃO DA VERSÃO 1.1 CONCLUÍDA!
==================================================
Autor: Anonymous

Novidades desta versão:
- Detecção automática de pastas sem Git.
- Atalho 'i' para inicializar o Git (git init) na pasta atual.
- Melhor tratamento de erros de comando.

Como usar:
1. Digite 'mygitui' em qualquer pasta.
2. Se a pasta não for um repositório, pressione 'i' para criar um.
3. Use TAB para navegar entre Status, Commits e Diff.
4. Pressione 'q' para sair.

Dica: Se o layout parecer estranho, use o comando 'tmux' antes.
==================================================
"
