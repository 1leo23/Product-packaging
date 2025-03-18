import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/brain_veiwer_card.dart';
import 'package:trajectory_app/cards/selet_record_card.dart';
import 'package:trajectory_app/data/record_data.dart';

class RecordsWidget extends StatefulWidget {
  const RecordsWidget({super.key});

  @override
  State<RecordsWidget> createState() => _RecordsWidgetState();
}

class _RecordsWidgetState extends State<RecordsWidget> {
  final data = RecordData();
  var viewerIndexList = <int>[];
  void _buildBrainViewer(int index) {
    setState(() {
      if (!viewerIndexList.contains(index)) viewerIndexList.add(index);
    });
  }

  void _popBrainViewer(int index) {
    setState(() {
      if (viewerIndexList.contains(index)) viewerIndexList.remove(index);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.topCenter, // 設定內容向上對齊,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 20),
        child: SingleChildScrollView(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              SelectRecordCard(buildBrainViewer: _buildBrainViewer, data: data),
              SizedBox(height: 18),
              ListView.builder(
                shrinkWrap: true, // ✅ 讓 ListView 只佔用實際內容的高度
                physics: NeverScrollableScrollPhysics(), // ✅ 禁止內部滾動，避免與外部滾動衝突
                reverse: true,
                itemCount: viewerIndexList.length,
                itemBuilder: (context, index) {
                  var record = data.recordList[viewerIndexList[index]];
                  return Column(
                    children: [
                      BrainViewerCard(
                        record: record,
                        recordIndex: viewerIndexList[index],
                        popBrainViewer: _popBrainViewer,
                      ),
                      SizedBox(height: 18),
                    ],
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
