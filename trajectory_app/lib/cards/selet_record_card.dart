import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/custom_card.dart';
import 'package:trajectory_app/const/constant.dart';
import 'package:trajectory_app/data/record_data.dart';
import 'package:trajectory_app/models/record_model.dart';

class SelectRecordCard extends StatefulWidget {
  final void Function(int) buildBrainViewer;
  final RecordData data;

  const SelectRecordCard({
    super.key,
    required this.buildBrainViewer,
    required this.data,
  });

  @override
  State<SelectRecordCard> createState() => _SelectRecordCardState();
}

class _SelectRecordCardState extends State<SelectRecordCard> {
  int selectedIndex = -1; // 紀錄當前選取的索引

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '選擇紀錄',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            SizedBox(height: 10),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: GridView.builder(
                shrinkWrap: true,
                physics: NeverScrollableScrollPhysics(),
                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 3,
                  crossAxisSpacing: 10,
                  mainAxisSpacing: 10,
                  childAspectRatio: 3,
                ),
                itemCount: widget.data.recordList.length,
                itemBuilder: (context, index) {
                  final record = widget.data.recordList[index];
                  return _buildRecordCard(record, index);
                },
              ),
            ),
            SizedBox(height: 20),
            _selectionButton(),
          ],
        ),
      ),
    );
  }

  Widget _buildRecordCard(RecordModel record, int index) {
    final isSelected = index == selectedIndex;

    return CustomCard(
      color: backgroundColor,
      borderColor: isSelected ? Colors.white : Colors.transparent,
      child: InkWell(
        onTap: () {
          setState(() {
            selectedIndex = index;
          });
        },
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 0, horizontal: 10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "${record.yyyy}年${record.mm}月${record.dd}日",
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

  Widget _selectionButton() {
    return Center(
      child: SizedBox(
        width: 200,
        child: ElevatedButton(
          onPressed: () {
            if (selectedIndex != -1) {
              widget.buildBrainViewer(selectedIndex);
            }
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: selectionColor,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
          child: Text(
            '選擇',
            style: TextStyle(fontSize: 18, color: Colors.white),
          ),
        ),
      ),
    );
  }
}
