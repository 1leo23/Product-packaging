import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/custom_card.dart';

class BrainViewerCard extends StatefulWidget {
  const BrainViewerCard({super.key});

  @override
  State<BrainViewerCard> createState() => _BrainViewerCard();
}

class _BrainViewerCard extends State<BrainViewerCard> {
  // 初始切片數字
  int axialSlice = 64;
  int coronalSlice = 96;
  int sagittalSlice = 64;

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      child: Column(
        children: [
          // 標題區
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '2022年02月28日',
                      style: TextStyle(color: Colors.white, fontSize: 16),
                    ),
                    Text(
                      '顱腔年齡 / 腦部年齡 : 62 / 71 歲',
                      style: TextStyle(color: Colors.white, fontSize: 16),
                    ),
                  ],
                ),
                IconButton(
                  icon: Icon(Icons.close, color: Colors.white),
                  onPressed: () {
                    Navigator.pop(context); // 關閉 widget
                  },
                ),
              ],
            ),
          ),
          // 影像區
          Expanded(
            child: Row(
              children: [
                _buildView('Axial', axialSlice, 'A', 'P'), // 軸向視圖
                _buildView('Coronal', coronalSlice, 'S', 'I'), // 冠狀視圖
                _buildView('Sagittal', sagittalSlice, 'S', 'I'), // 矢狀視圖
              ],
            ),
          ),
        ],
      ),
    );
  }

  // 構建單個視圖的函數
  Widget _buildView(
    String viewType,
    int slice,
    String topLabel,
    String bottomLabel,
  ) {
    return Expanded(
      child: Stack(
        alignment: Alignment.center,
        children: [
          // MRI 影像（這裡使用占位符，需替換為實際影像）
          Container(
            color: Colors.grey[800], // 假設的影像背景
            child: Center(
              child: Text(
                '$viewType View', // 占位符，顯示視圖名稱
                style: TextStyle(color: Colors.white),
              ),
            ),
          ),
          // 十字線
          Positioned(
            top: 0,
            bottom: 0,
            left: 0,
            right: 0,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(topLabel, style: TextStyle(color: Colors.blue)),
                Container(height: 1, color: Colors.blue), // 水平線
                Expanded(child: Center()),
                Container(height: 1, color: Colors.blue), // 垂直線（模擬效果）
                Text(bottomLabel, style: TextStyle(color: Colors.blue)),
              ],
            ),
          ),
          Positioned(
            left: 0,
            right: 0,
            child: Container(width: 1, color: Colors.blue), // 垂直線
          ),
          // 導航控制
          Positioned(
            bottom: 16,
            child: Row(
              children: [
                IconButton(
                  icon: Icon(Icons.remove, color: Colors.white),
                  onPressed: () {
                    setState(() {
                      if (viewType == 'Axial') axialSlice--;
                      if (viewType == 'Coronal') coronalSlice--;
                      if (viewType == 'Sagittal') sagittalSlice--;
                    });
                  },
                ),
                Text('$slice', style: TextStyle(color: Colors.white)),
                IconButton(
                  icon: Icon(Icons.add, color: Colors.white),
                  onPressed: () {
                    setState(() {
                      if (viewType == 'Axial') axialSlice++;
                      if (viewType == 'Coronal') coronalSlice++;
                      if (viewType == 'Sagittal') sagittalSlice++;
                    });
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
