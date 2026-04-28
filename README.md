# ComfyUI-LightQueueCounter

ComfyUIのバックエンド・キューの数を、生成速度を一切損なうことなくリアルタイムで表示するための超軽量カスタムノードじゃ！

## 特徴

- **圧倒的な軽さ**: 1回の実行にかかる時間はわずか **0.004s** 前後。単純な文字列結合と同等の負荷で動作するぞ。
- **UIを邪魔しない**: ノードを折りたたむことで、タイトル部分に現在のキュー数を表示できる。
- **柔軟な表示モード**: おぬしの好みに合わせて、以下の3種類から表示を選べるぞ。
  - `total`: 合計数のみ表示
  - `short`: 実行中/待機中/合計を表示
  - `full`: 詳細なステータスを表示

## 導入方法

ComfyUIの `custom_nodes` ディレクトリで、以下のコマンドを打ち込むのじゃ！

```bash
git clone [https://github.com/ruminar/ComfyUI-LightQueueCounter.git](https://github.com/ruminar/ComfyUI-LightQueueCounter.git)
```

## 使い方

以下の3つのノードが追加されるぞ：
3の、**Light Queue Counter Title Tap** を使うのがおすすめじゃ

1. **Light Queue Counter Any Passthrough**: 任意のデータの流れに差し込んで、現在のキュー数を取得する。
2. **Light Queue Counter Set Title**: 文字列を受け取り、自分自身のノードタイトルに設定する。
3. **Light Queue Counter Title Tap**: 任意の値をトリガーにして、キュー数を読み取りタイトルに表示する（メインの配線を汚したくない時に便利じゃ！）。

## ライセンス

GPL-3.0（ComfyUI本体の掟に従っておるぞ！）
