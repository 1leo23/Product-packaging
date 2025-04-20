import 'dart:async';
import 'dart:io';

import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/custom_card.dart';
import 'package:trajectory_app/models/record_model.dart';
import 'package:trajectory_app/services/api_service.dart';

class BrainViewerCard extends StatefulWidget {
  final String memberId;
  final RecordModel record;
  final int recordIndex;
  final void Function(int) popBrainViewer;

  const BrainViewerCard({
    super.key,
    required this.record,
    required this.recordIndex,
    required this.popBrainViewer,
    required this.memberId,
  });

  @override
  State<BrainViewerCard> createState() => _BrainViewerCardState();
}

class _BrainViewerCardState extends State<BrainViewerCard> {
  Map<String, List<File>>? imageSet;
  final Map<String, int> sliceIndex = {'axial': 0, 'coronal': 0, 'sagittal': 0};
  final Map<String, int> sliceMax = {'axial': 0, 'coronal': 0, 'sagittal': 0};

  Timer? _longPressTimer;

  @override
  void initState() {
    super.initState();
    _loadSlices();
  }

  Future<void> _loadSlices() async {
    try {
      final result = await ApiService.fetchAndUnzipSlices(
        widget.memberId,
        widget.recordIndex + 1, // 資料庫紀錄從1開始
      );

      // 預先載入所有圖片
      for (final plane in ['axial', 'coronal', 'sagittal']) {
        final imageList = result[plane] ?? [];
        for (final file in imageList) {
          await precacheImage(FileImage(file), context);
        }
      }

      if (!mounted) return;
      setState(() {
        imageSet = result;
        for (var plane in ['axial', 'coronal', 'sagittal']) {
          sliceMax[plane] = result[plane]?.length ?? 0;
          sliceIndex[plane] = (sliceMax[plane]! / 2).toInt();
        }
      });
    } catch (e) {
      print("❌ 載入切片失敗：$e");
    }
  }

  void _startLongPressTimer(String label, bool isIncrement) {
    _longPressTimer = Timer.periodic(const Duration(milliseconds: 20), (_) {
      setState(() {
        final value = sliceIndex[label]!;
        final max = sliceMax[label]!;
        if (isIncrement && value < max - 1) {
          sliceIndex[label] = value + 1;
        } else if (!isIncrement && value > 0) {
          sliceIndex[label] = value - 1;
        }
      });
    });
  }

  void _stopLongPressTimer() {
    _longPressTimer?.cancel();
    _longPressTimer = null;
  }

  Widget _buildSliceControl(String label) {
    final value = sliceIndex[label]!;
    final max = sliceMax[label]!;

    return Column(
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 8),
        Listener(
          onPointerSignal: (pointerSignal) {
            if (pointerSignal is PointerScrollEvent && imageSet != null) {
              setState(() {
                if (pointerSignal.scrollDelta.dy < 0 && value > 0) {
                  // 滾輪往上：減少切片
                  sliceIndex[label] = value - 1;
                } else if (pointerSignal.scrollDelta.dy > 0 &&
                    value < max - 1) {
                  // 滾輪往下：增加切片
                  sliceIndex[label] = value + 1;
                }
              });
            }
          },

          child: Container(
            width: 230,
            height: 230,
            decoration: BoxDecoration(
              color: Colors.black,
              image:
                  (imageSet != null &&
                          imageSet![label]!.isNotEmpty &&
                          value < max)
                      ? DecorationImage(
                        image: FileImage(imageSet![label]![value]),
                        fit: BoxFit.cover,
                      )
                      : null,
            ),
            child:
                (imageSet == null)
                    ? const Center(
                      child: CircularProgressIndicator(color: Colors.white),
                    )
                    : null,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            GestureDetector(
              onLongPressStart: (_) => _startLongPressTimer(label, false),
              onLongPressEnd: (_) => _stopLongPressTimer(),
              child: IconButton(
                onPressed:
                    () => setState(() {
                      if (value > 0) sliceIndex[label] = value - 1;
                    }),
                icon: const Icon(Icons.remove, color: Colors.white),
                style: IconButton.styleFrom(backgroundColor: Colors.grey[800]),
              ),
            ),
            const SizedBox(width: 8),
            SizedBox(
              width: 60,
              child: Center(
                child: Text(
                  value.toString(),
                  style: const TextStyle(fontSize: 18, color: Colors.white),
                ),
              ),
            ),
            const SizedBox(width: 8),
            GestureDetector(
              onLongPressStart: (_) => _startLongPressTimer(label, true),
              onLongPressEnd: (_) => _stopLongPressTimer(),
              child: IconButton(
                onPressed:
                    () => setState(() {
                      if (value < max - 1) sliceIndex[label] = value + 1;
                    }),
                icon: const Icon(Icons.add, color: Colors.white),
                style: IconButton.styleFrom(backgroundColor: Colors.grey[800]),
              ),
            ),
          ],
        ),
      ],
    );
  }

  @override
  void dispose() {
    _stopLongPressTimer();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const SizedBox(width: 40),
              Column(
                children: [
                  Text(
                    "${widget.record.yyyy}年${widget.record.mm}月${widget.record.dd}日",
                    style: const TextStyle(fontSize: 16, color: Colors.white),
                  ),
                  Text(
                    "實際年齡 / 腦部年齡：${widget.record.actualAge} / ${widget.record.brainAge} 歲",
                    style: const TextStyle(fontSize: 14, color: Colors.white),
                  ),
                ],
              ),
              IconButton(
                onPressed: () => widget.popBrainViewer(widget.recordIndex),
                icon: const Icon(Icons.close, color: Colors.white, size: 24),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSliceControl("axial"),
              _buildSliceControl("coronal"),
              _buildSliceControl("sagittal"),
            ],
          ),
        ],
      ),
    );
  }
}
