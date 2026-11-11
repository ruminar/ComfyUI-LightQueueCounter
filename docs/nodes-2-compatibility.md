# Legacy Nodes / Nodes 2.0 互換性調査

調査日: 2026-11-12。実機のComfyUIによる描画・実行確認は未実施。

追記: 修正後、ユーザーから「動作確認しましたがOKっぽいです」との報告あり。
描画方式・バージョン・確認項目の内訳は未記録のため、以下の手動確認表は項目別の確認済み記録には更新していない。エージェント自身による実機確認は未実施。

## 公式実装の確認範囲

- GitHubの最新公開Releaseは [v1.60.0](https://github.com/Comfy-Org/ComfyUI_frontend/releases/tag/v1.60.0)（2026-10-26公開）。
- 現行mainは `e8791746d266a3e7da22c64eab88225341dc0fb0`。package.jsonの版は1.61.0。
- Nodes 2.0はVueによる描画方式への変更である。[公式案内](https://blog.comfy.org/p/comfyui-node-2-0)
- [mainの実行イベント処理](https://github.com/Comfy-Org/ComfyUI_frontend/blob/e8791746d266a3e7da22c64eab88225341dc0fb0/src/scripts/app.ts#L778)と[v1.60.0の同処理](https://github.com/Comfy-Org/ComfyUI_frontend/blob/v1.60.0/src/scripts/app.ts#L790)では、描画方式の分岐なしに、実行IDから対象ノードを解決し `node.onExecuted(detail.output)` を呼ぶ。`display_node`、サブグラフ、アクティブWorkflowの判定もフロントエンドが扱う。
- [ノードID移行資料](https://github.com/Comfy-Org/ComfyUI_frontend/blob/e8791746d266a3e7da22c64eab88225341dc0fb0/docs/extensions/node-id-migration.md)は、フロントエンド内部のノードIDを文字列として扱うよう求めている。
- [LGraphNodeのtitleアクセサ](https://github.com/Comfy-Org/ComfyUI_frontend/blob/e8791746d266a3e7da22c64eab88225341dc0fb0/src/lib/litegraph/src/LGraphNode.ts#L463)は状態更新を通知する。[Vue側のタイトル編集](https://github.com/Comfy-Org/ComfyUI_frontend/blob/e8791746d266a3e7da22c64eab88225341dc0fb0/src/renderer/extensions/vueNodes/composables/useNodeEventHandlers.ts)も `node.title = newTitle` を使用する。v1.60.0にも同じtitleアクセサがある。独自DOM操作やVueストアへの直接アクセスは不要と判断した。
- [ウィジェット値の更新処理](https://github.com/Comfy-Org/ComfyUI_frontend/blob/e8791746d266a3e7da22c64eab88225341dc0fb0/src/core/graph/widgets/nodeWidgetValues.ts)は `widget.value` を設定してから `widget.callback` を呼ぶ。現在のコールバック処理は値を読み直すため維持する。
- [公式バックエンドのPromptQueue](https://github.com/Comfy-Org/ComfyUI/blob/master/execution.py)に `mutex`、`queue`、`currently_running` と既存のフォールバックメソッドがあることを確認した。キュー取得は描画方式に依存しないため変更不要と判断した。

## 修正と維持した仕様

`web/light_queue_counter_title.js` の実行結果の受信経路だけを変更した。
グローバルな `executed` リスナーで `Number(nodeId)` を使って `app.graph` を探索する処理を、Title Tap / Set Titleの `onExecuted` に置き換えた。
数値化・現在表示中のグラフへの依存をなくし、対象の解決をComfyUIに委ねる。
これは従来方式でも使われるノード実行コールバックであり、Nodes 2.0専用の分岐を追加する必要はない。
既存の `onExecuted` は先に呼び、引数・this・戻り値を維持する。

`node.title` への代入、Legacy用の再描画要求、label / title_formatの変更処理、タイトル書式、APIからのUIペイロードは維持した。
Pythonコード、登録ノードID、入力名、出力名・型・順序、デフォルト値、ANYパススルー、コンソール出力、毎回実行する条件は変更していない。V3 APIへの移行も行っていない。

なお、[公式フック資料](https://docs.comfy.org/custom-nodes/js/javascript_hooks)はprototypeの既存メソッドを包む一般的な手法について将来的な変更リスクを記載している。本修正は現行公式実装が呼ぶ `onExecuted` に限定し、既存のbeforeRegisterNodeDef / onNodeCreated構造は保った。将来版までの保証を意味しない。

## 実施済みのローカルテスト

Node.js v24.18.0 / Python 3.14.6、追加依存なし。

```powershell
node --test tests/title.test.mjs
python -B -m unittest discover -s tests -p test_nodes.py -v
git diff --check
```

- JavaScript: 8テスト成功。対象インスタンスへの更新、title setterへの代入、全書式、labelの即時反映、コールバックの連鎖・重複防止、Set Title、未定義widgets、無関係な出力の無視、対象外ノードを検証。
- Python: 5テスト成功。キュー取得とフォールバック、登録・入出力契約、パススルーの同一オブジェクト保持、全書式と件数、UIペイロード、コンソール出力、Set Titleの整形、IS_CHANGEDを検証。
- `git diff --check`: 成功。

JavaScriptはappをスタブ化して拡張を実行し、Pythonはserverモジュールをスタブ化している。実際のVue描画、LiteGraph描画、WebSocket配送、ComfyUIの型検証・キャッシュ・Workflow復元を検証したものではない。実機再現によってNodes 2.0固有の表示不具合を確認したわけではなく、公式ソース調査から実行結果の受信経路に互換性上の問題を見つけて修正した。

## 実機で必要な手動確認

テスト前にComfyUI本体・フロントエンドの版を記録する。設定のNodes 2.0（内部キー `Comfy.VueNodes.Enabled`）を切り替え、必要に応じ再読み込みする。以下を両方の方式で実施する。

| 項目・操作 | 期待結果 | Legacy | Nodes 2.0 |
| --- | --- | --- | --- |
| 修正前に保存した3ノードを含むWorkflowを読み込む | ノード欠落なし。ID、配線、値、入力名、出力名・順序が維持される | 未実施 | 未実施 |
| Title Tapを接続して実行。展開・折りたたみの両状態で確認 | 実行時点のタイトルが表示される。再実行で更新される | 未実施 | 未実施 |
| 実行後にlabelとtotal / short / fullを変更 | 次の実行を待たず最新結果でタイトル更新。空白labelはqueueになる | 未実施 | 未実施 |
| Any Passthroughのtitle / statusをSet Titleへ接続 | Set TitleのタイトルとSTRING出力が一致。改行は空白になる | 未実施 | 未実施 |
| STRING、IMAGE、LATENT等をAny Passthroughへ接続 | 型検証を通り、後続処理に同じ値が渡る。6出力が既存の順序で利用できる | 未実施 | 未実施 |
| 複数のキューを投入して実行、print_to_consoleを切り替える | 実行時のrunning / pending / totalが整合し、コンソール出力の有無が切り替わる | 未実施 | 未実施 |
| 同じ入力でTitle Tap / Set Titleを繰り返し実行 | 表示用ノードが毎回更新される。Any Passthroughの既存キャッシュ挙動は維持される | 未実施 | 未実施 |
| 複数のTitle Tap / Set Titleを配置 | 実行対象のノードのみ更新される | 未実施 | 未実施 |
| 実行中に別Workflowタブへ切り替える | 別Workflowの同じIDのノードを誤って更新しない | 未実施 | 未実施 |
| サブグラフ対応版で内部に表示ノードを配置し、内外の表示状態で実行 | 正しい内部ノードが更新される。別ノードを変更しない | 未実施 | 未実施 |
| 実行後に保存・再読み込みし、再実行と書式変更を行う | タイトル、配線、ウィジェット値が復元され、再実行後も更新可能 | 未実施 | 未実施 |

件数はノード実行時のスナップショットである。実行中のジョブを含むため、処理終了後のQueue表示と一致しない場合がある。キュー変更だけではタイトルは更新されない。最新結果の保持は従来どおりメモリ上のみで、再読み込み後に書式を即時反映させるには一度実行する必要がある。
