# -*- mode: python -*-

block_cipher = None

a = Analysis(['/Users/oracle/Desktop/vm/main.py'],
             pathex=['/Users/oracle/Desktop/vm'],
             binaries=[],
             datas=[('/Users/oracle/Desktop/vm/migration.kv', '.'),
                    ('/Users/oracle/Desktop/vm/data/logo.png', 'data'),
                    ('/Users/oracle/Desktop/vm/data/help/oci.png', 'data/help'),
                    ('/Users/oracle/Desktop/vm/data/help/vm.png', 'data/help'),
                    ('/Users/oracle/Desktop/vm/data/status/failed.png', 'data/status'),
                    ('/Users/oracle/Desktop/vm/data/status/pending.png', 'data/status'),
                    ('/Users/oracle/Desktop/vm/data/status/success.png', 'data/status'),
                    ('/Users/oracle/Desktop/vm/data/icon.ico', 'data')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['_tkinter', 'Tkinter', 'enchant', 'twisted'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='MigrationTool',
          debug=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Migration Tool')
app = BUNDLE(coll,
             name='MigrationTool.app',
             icon='/Users/oracle/Desktop/vm/data/icon.ico',
             bundle_identifier=None)
