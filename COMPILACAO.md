# 📦 Compilação do Sistema de Automação MT5

## 🚀 Método Rápido (Recomendado)

### Opção 1: Script Automático
Execute o arquivo `compilar.bat` (clique duplo ou via terminal):
```cmd
compilar.bat
```

O script irá:
- ✅ Verificar dependências
- ✅ Limpar builds anteriores
- ✅ Compilar o executável
- ✅ Mover para pasta raiz
- ✅ Limpar arquivos temporários

Resultado: `AutomacaoMT5.exe` (~50-80 MB)

---

## 🔧 Método Manual

### 1. Instalar PyInstaller
```cmd
pip install pyinstaller
```

### 2. Compilar usando o spec file
```cmd
pyinstaller --clean --noconfirm build_exe.spec
```

### 3. Executável estará em
```
dist\AutomacaoMT5.exe
```

---

## 📋 Opções de Compilação Avançadas

### Executável único (onefile) - Mais simples de distribuir
```cmd
pyinstaller --onefile --name=AutomacaoMT5 --add-data="config.ini;." --add-data="coordenadas.json;." starter.py
```

### Com ícone personalizado
```cmd
pyinstaller --onefile --icon=icone.ico --name=AutomacaoMT5 starter.py
```

### Sem console (janela GUI apenas)
```cmd
pyinstaller --onefile --noconsole --name=AutomacaoMT5 starter.py
```

---

## 📦 Criar Instalador (Opcional)

### Usando Inno Setup (Windows)

1. Baixe [Inno Setup](https://jrsoftware.org/isdl.php)
2. Crie arquivo `installer.iss`:

```iss
[Setup]
AppName=Sistema de Automação MT5
AppVersion=2.0
DefaultDirName={pf}\AutomacaoMT5
DefaultGroupName=Automação MT5
OutputDir=installers
OutputBaseFilename=AutomacaoMT5_Setup

[Files]
Source: "AutomacaoMT5.exe"; DestDir: "{app}"
Source: "config.ini"; DestDir: "{app}"
Source: "README.md"; DestDir: "{app}"

[Icons]
Name: "{group}\Automação MT5"; Filename: "{app}\AutomacaoMT5.exe"
Name: "{commondesktop}\Automação MT5"; Filename: "{app}\AutomacaoMT5.exe"
```

3. Compile com Inno Setup Compiler

---

## ⚠️ Notas Importantes

### Arquivos Necessários
O executável precisa dos seguintes arquivos na mesma pasta:
- ✅ `config.ini` - Configurações do sistema
- ✅ `coordenadas.json` - Coordenadas calibradas (opcional)
- ✅ Pasta `sets/` - Arquivos .set para processar

### Antivírus
Alguns antivírus podem bloquear o executável. Adicione exceção se necessário.

### Tamanho do Executável
- **Onefile**: ~50-80 MB (tudo incluído)
- **Onedir**: ~30 MB + pasta com DLLs

### Performance
- Executável pode ser ~2-3s mais lento no startup vs Python
- Performance em runtime é idêntica

---

## 🔍 Troubleshooting

### Erro: "PyInstaller not found"
```cmd
pip install pyinstaller
```

### Erro: "Module not found" no executável
Adicione ao `hiddenimports` no arquivo `.spec`:
```python
hiddenimports=['modulo_faltando'],
```

### Executável muito grande
Use UPX para compressão:
```cmd
pyinstaller --upx-dir=C:\upx starter.py
```

### Testar executável
```cmd
.\AutomacaoMT5.exe
```

---

## 📊 Comparação de Métodos

| Método | Tamanho | Velocidade | Facilidade |
|--------|---------|------------|------------|
| Script .bat | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| PyInstaller manual | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Inno Setup | ⭐ | ⭐⭐⭐ | ⭐ |

**Recomendação**: Use `compilar.bat` para compilação rápida e fácil!
