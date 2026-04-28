# ComfyUI-LightQueueCounter

ComfyUIのバックエンド・キューの数を、ワークフロー実行時に軽量表示するカスタムノードじゃ！

## 特徴

- **圧倒的な軽さ**: 1回の実行にかかる時間はわずか **0.004s** 前後（注：作者環境で速いとき）。単純な文字列結合と同等の負荷で動作するぞ。
- **UIを邪魔しない**: ノードを折りたたむことで、タイトル部分に実行時点のキュー数を表示できる。
- **柔軟な表示モード**: おぬしの好みに合わせて、以下の3種類から表示を選べるぞ。
  - `total`: 合計数のみ表示
  - `short`: 実行中/待機中/合計を表示
  - `full`: 詳細なステータスを表示

<img width="493" height="221" alt="fabc9b7a-8f44-4be1-b44c-f12a0ebd1823" src="https://github.com/user-attachments/assets/f91ed035-35c5-4d8e-b079-c0168b6fb5f2" />

## 導入方法

ComfyUIの `custom_nodes` ディレクトリで、以下のコマンドを打ち込むのじゃ！

```bash
git clone https://github.com/ruminar/ComfyUI-LightQueueCounter.git
```

## 使い方

まずは、3つ目の **Light Queue Counter Title Tap** を使うのがおすすめじゃ。  
適当なノードからぶら下げて「折りたたみ表示」すると、タイトル部分にキュー件数が表示されるのじゃ。

<img width="266" height="164" alt="cd33e1ce-94d9-4f0e-ae27-e9808909f5e7" src="https://github.com/user-attachments/assets/1e87ac6f-132c-4eb7-83a9-358f153074bd" />

<br>

以下の3つのノードが追加されるぞ：

1. **Light Queue Counter Any Passthrough**: 任意のデータの流れに差し込んで、実行時点のキュー数を取得する。

2. **Light Queue Counter Set Title**: 文字列を受け取り、自分自身のノードタイトルに設定する。

3. **Light Queue Counter Title Tap**: 任意の値をトリガーにして、キュー数を読み取りタイトルに表示する（メインの配線を汚したくない時に便利じゃ！）。

<br>

<img width="437" height="170" alt="38dcafd5-822e-45e5-a563-48c0f01b2842" src="https://github.com/user-attachments/assets/a8a265dd-fc0d-45fc-a867-fcc65753fdde" />


「適当なノードにぶら下げて、折りたたんでおくとタイトルにキュー件数が表示されます」  
「プッシュ方式で起動し、文字列結合と同等の速さで動作するため、GPU処理を邪魔しにくいです」

## ライセンス

GPL-3.0（ComfyUI本体の掟に従っておるぞ！）
