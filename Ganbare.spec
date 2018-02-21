# -*- mode: python -*-
# from kivy import kivy_data_dir

block_cipher = None

a = Analysis(['main.py'],
             pathex=['/home/ubuntu/Oracle/vm-migration'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['cv2', 'enchant'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

# kivy_assets_toc = [Tree(kivy_data_dir, prefix=('data'))]

a.datas += [('migration.kv', '/home/ubuntu/Oracle/vm-migration/migration.kv', 'DATA')]
# a.datas += [('logo.png', '/home/ubuntu/Oracle/vm-migration/data/logo.png', 'DATA')]

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Ganbare',
          debug=False,
          strip=False,
          upx=True,
          console=True, icon='x-7.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               # *kivy_assets_toc,
               strip=False,
               upx=True,
               name='Ganbare')
