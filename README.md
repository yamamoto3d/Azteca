<h2>What`s This</h2>
<div>個人的なMaya用スクリプト</div>

<h2>お品書き</h2>
<div>
    <ul>
        <li>Build and export:ゲーム用の書き出しだけでなく,Substance用ハイポリ・ローポリなど複数の出力を想定した書き出しツール。書き出し前の事前処理とテクスチャフォルダの同期も可能</li>
        <li>Set subdivision level:サブディビジョンプレビューのレベルの変更を複数のメッシュで一括して行う</li>
        <li>Create camera projection material:カメラを選択して実行すると、カメラからテクスチャを投影するマテリアルを作成する。メッシュも選択すると自動でアサインされる。（主にAI画像リファレンス用）
        <li>Focal Length Up/Down:モデルビューにセットされているパースペクティブの焦点距離を単焦点レンズでメジャーな値でステップ変更する。16/24/35/50/85/135/200（ホットキー登録想定）</li>
    </ul>
</div>
<h2>注意点</h2>
<p>Win11以降、OneDriveにドキュメントフォルダが管理されるようになったせいで,FBXエクスポートが動かなくなりました。
OneDriveのドキュメント共有を停止するか、Mayaフォルダーを別の場所に変更してください</p>
<blockquote>
    <a href="https://www.autodesk.co.jp/support/technical/article/caas/sfdcarticles/sfdcarticles/JPN/Write-settings-failed-when-exporting-objects-with-the-game-exporter-in-Maya-LT.html">
        <p>MayaおよびMaya LTのゲームエクスポータを使用してオブジェクトを書き出す場合に「設定の書き込みに失敗しました」</p>
    </a>
</blockquote>
<h2>インストール</h2>
<ol>
<li>ダウンロードまたはPULLして適当なフォルダーに保存</li>
<li>userSetup.pyを既存のMayaスクリプトフォルダー追加</li>
<li>二行目に本体を配置したパスに書き換える</li>
<li>Maya起動。メニューが出てくるので実行コマンドはシェルフ登録などで確認できます</li>
</ol>