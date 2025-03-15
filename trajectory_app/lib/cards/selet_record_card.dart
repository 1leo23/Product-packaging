import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/custom_card.dart';
import 'package:trajectory_app/const/constant.dart';
import 'package:trajectory_app/data/record_data.dart';
import 'package:trajectory_app/models/record_model.dart';

class SelectRecordCard extends StatefulWidget {
  @override
  State<SelectRecordCard> createState() => _SelectRecordCardState();
}

class _SelectRecordCardState extends State<SelectRecordCard> {
  // 假設的紀錄數據，根據圖片提供的值
  int selectedIndex = -1;
  final data = RecordData();
  @override
  Widget build(BuildContext context) {
    return CustomCard(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 標題
            Text(
              '選擇紀錄',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            SizedBox(height: 10), // 增加間距
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: GridView.builder(
                shrinkWrap: true, // 避免佔用過多空間
                physics: NeverScrollableScrollPhysics(), // 禁用滾動
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3, // 2 列
                  crossAxisSpacing: 10, // 水平間距
                  mainAxisSpacing: 10, // 垂直間距
                  childAspectRatio: 3, // 調整卡片寬高比
                ),
                itemCount: data.recordList.length,
                itemBuilder: (context, index) {
                  final record = data.recordList[index];
                  return _buildRecordCard(record, index);
                },
              ),
            ),
            SizedBox(height: 20), // 按鈕前的間距
            // 選擇按鈕
            _selectionButton(),
          ],
        ),
      ),
    );
  }

  // 單個紀錄卡片
  Widget _buildRecordCard(RecordModel record, int index) {
    final isSelected = index == selectedIndex;

    return CustomCard(
      color: backgroundColor,
      borderColor: isSelected ? Colors.white : Colors.transparent,
      child: InkWell(
        onTap:
            () => setState(() {
              selectedIndex = index;
            }),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 0, horizontal: 10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "${record.yyyy}年${record.mm}月${record.dd}日 ",
                style: TextStyle(color: Colors.white, fontSize: 14),
              ),

              SizedBox(height: 5),
              Text(
                '實際年齡 / 腦部年齡 : ${record.actualAge} / ${record.brainAge}歲',
                style: TextStyle(color: Colors.white, fontSize: 12),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

Center _selectionButton() {
  return Center(
    child: Container(
      width: 200,
      child: ElevatedButton(
        onPressed: () {
          // TODO: 實現選擇邏輯，例如返回選中的紀錄
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: selectionColor, // 按鈕背景色
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8), // 圓角
          ),
        ),
        child: Text('選擇', style: TextStyle(fontSize: 18, color: Colors.white)),
      ),
    ),
  );
}
