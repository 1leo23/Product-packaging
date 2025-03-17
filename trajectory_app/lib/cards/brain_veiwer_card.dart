import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/custom_card.dart';
import 'package:trajectory_app/models/record_model.dart';

class BrainViewerCard extends StatefulWidget {
  final RecordModel record;
  final int recordIndex;
  final void Function(int) popBrainViewer;
  const BrainViewerCard({
    super.key,
    required this.record,
    required this.recordIndex,
    required this.popBrainViewer,
  });

  @override
  State<BrainViewerCard> createState() => _BrainViewerCardState();
}

class _BrainViewerCardState extends State<BrainViewerCard> {
  // 初始切片數
  int axialSlice = 64;
  int coronalSlice = 96;
  int sagittalSlice = 64;

  // 建立切片控制元件
  Widget _buildSliceControl(
    String label,
    int value,
    ValueChanged<String> onChanged,
    VoidCallback onDecrease,
    VoidCallback onIncrease,
  ) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        SizedBox(height: 8),
        Container(
          width: 230,
          height: 230,
          decoration: BoxDecoration(
            color: Colors.black,
            image: DecorationImage(
              image: AssetImage('assets/mri_placeholder.png'),
              fit: BoxFit.cover,
            ),
          ),
        ),
        SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            IconButton(
              onPressed: onDecrease,
              icon: Icon(Icons.remove, color: Colors.white),
              style: IconButton.styleFrom(backgroundColor: Colors.grey[800]),
            ),
            SizedBox(width: 8),
            SizedBox(
              width: 60,
              child: TextField(
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 18, color: Colors.white),
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  filled: true,
                  fillColor: Colors.grey[900],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide.none,
                  ),
                ),
                onChanged: onChanged,
                controller: TextEditingController(text: value.toString()),
              ),
            ),
            SizedBox(width: 8),
            IconButton(
              onPressed: onIncrease,
              icon: Icon(Icons.add, color: Colors.white),
              style: IconButton.styleFrom(backgroundColor: Colors.grey[800]),
            ),
          ],
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      padding: EdgeInsets.all(20),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // 標題區域
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              SizedBox(width: 40),
              Column(
                children: [
                  Text(
                    "${widget.record.yyyy}年${widget.record.mm}月${widget.record.dd}日",
                    style: TextStyle(fontSize: 16, color: Colors.white),
                  ),
                  Text(
                    "實際年齡 / 腦部年齡：${widget.record.actualAge} / ${widget.record.brainAge} 歲",
                    style: TextStyle(fontSize: 14, color: Colors.white),
                  ),
                ],
              ),
              IconButton(
                onPressed: () {
                  widget.popBrainViewer(widget.recordIndex);
                },
                icon: Icon(Icons.close, color: Colors.white, size: 24),
              ),
            ],
          ),
          SizedBox(height: 16),

          // MRI 影像顯示區域
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSliceControl(
                "Axial",
                axialSlice,
                (value) {
                  setState(() {
                    axialSlice = int.tryParse(value) ?? axialSlice;
                  });
                },
                () {
                  setState(() {
                    if (axialSlice > 0) axialSlice--;
                  });
                },
                () {
                  setState(() {
                    axialSlice++;
                  });
                },
              ),
              _buildSliceControl(
                "Coronal",
                coronalSlice,
                (value) {
                  setState(() {
                    coronalSlice = int.tryParse(value) ?? coronalSlice;
                  });
                },
                () {
                  setState(() {
                    if (coronalSlice > 0) coronalSlice--;
                  });
                },
                () {
                  setState(() {
                    coronalSlice++;
                  });
                },
              ),
              _buildSliceControl(
                "Sagittal",
                sagittalSlice,
                (value) {
                  setState(() {
                    sagittalSlice = int.tryParse(value) ?? sagittalSlice;
                  });
                },
                () {
                  setState(() {
                    if (sagittalSlice > 0) sagittalSlice--;
                  });
                },
                () {
                  setState(() {
                    sagittalSlice++;
                  });
                },
              ),
            ],
          ),
          //SizedBox(height: 16),
        ],
      ),
    );
  }
}
