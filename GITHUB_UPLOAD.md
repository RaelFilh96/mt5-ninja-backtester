# 📤 Instruções para Subir no GitHub

## Passo 1: Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name:** `mt5-ninja-backtester`
   - **Description:** Sistema de automação inteligente para backtests no MetaTrader 5
   - **Visibility:** Public (ou Private se preferir)
   - ❌ NÃO marque "Add a README file"
   - ❌ NÃO marque "Add .gitignore"
   - ❌ NÃO marque "Choose a license"
3. Clique em **Create repository**

## Passo 2: Conectar ao Repositório Remoto

Após criar, o GitHub mostrará comandos. Execute no terminal:

```bash
cd "c:\Users\Israel Filho\OneDrive\AUTOMACAO MT5\wfa\auto-backtesting-20250922T001018Z-1-001\auto-backtesting"

# Substitua SEU_USUARIO pelo seu username do GitHub
git remote add origin https://github.com/SEU_USUARIO/mt5-ninja-backtester.git

# Enviar para o GitHub
git push -u origin main
```

## Passo 3: Criar Release (Opcional)

Para disponibilizar o .exe para download:

1. No GitHub, vá em **Releases** (lado direito)
2. Clique em **Create a new release**
3. Tag: `v3.0.0`
4. Title: `MT5 Ninja Backtester v3.0 - Monitor Híbrido`
5. Descrição:
```
## 🆕 Novidades
- Monitor híbrido v3.0 (Porta + CPU)
- Detecção de início via conexão porta 3000
- Detecção de fim via CPU do metatester64
- Fallback automático

## 📥 Download
- `MT5_Ninja_Backtester.exe` - Executável completo (~31 MB)
```
6. Arraste o arquivo `MT5_Ninja_Backtester.exe` para a área de upload
7. Clique em **Publish release**

## ✅ Pronto!

Seu projeto estará disponível em:
```
https://github.com/SEU_USUARIO/mt5-ninja-backtester
```

---

## 🔧 Comandos Git Úteis

```bash
# Ver status
git status

# Ver histórico
git log --oneline

# Atualizar repositório remoto
git push

# Baixar atualizações
git pull
```
