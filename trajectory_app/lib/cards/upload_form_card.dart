import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/custom_card.dart';

class UploadFormCard extends StatefulWidget {
  final void Function(String memberId)?
  loadUploadFromMemberPreview; // 為了預覽當先選定成員
  const UploadFormCard({super.key, required this.loadUploadFromMemberPreview});

  @override
  State<UploadFormCard> createState() => _UploadFormCardState();
}

class _UploadFormCardState extends State<UploadFormCard> {
  final _idController = TextEditingController();
  final _idFocusNode = FocusNode();
  final _dateController = TextEditingController();
  final _fileController = TextEditingController();
  final _actualAgeController = TextEditingController();
  final _brainAgeController = TextEditingController();
  final _riskScoreController = TextEditingController();

  void dispose() {
    _idController.dispose();
    _idFocusNode.dispose();
    _dateController.dispose();
    _fileController.dispose();
    _actualAgeController.dispose();
    _brainAgeController.dispose();
    _riskScoreController.dispose();
    widget.loadUploadFromMemberPreview?.call('');
    super.dispose();
  }

  @override
  void initState() {
    super.initState();

    _idFocusNode.addListener(() {
      if (!_idFocusNode.hasFocus) {
        String memberId = _idController.text;
        widget.loadUploadFromMemberPreview?.call(memberId);
        print("偵測id輸入成功");
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      width: 500,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 50, vertical: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '上傳影像',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            _buildInputRow(
              '身份證字號',
              '身份證字號',
              true,
              controller: _idController,
              focusNode: _idFocusNode,
            ),
            _buildInputRow('拍攝日期', 'YYYY/MM/DD', true),
            _buildInputRow('上傳檔案', '上傳檔案 nii.gz', true),
            _buildInputRow('認知測驗', '認知測驗成績(0~100)', true),
            _buildInputRow('實際年齡', '實際年齡 (自動填入)', false),
            _buildInputRow('腦部年齡', '腦部年齡 (AI計算)', false),
            _buildInputRow('失智症風險', '失智症風險 (AI計算)', false),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(flex: 2, child: _buildButton('建檔', 2)),
                const SizedBox(width: 5),
                const Icon(Icons.double_arrow),
                const SizedBox(width: 5),
                Expanded(flex: 2, child: _buildButton('AI計算', 1)),
                const SizedBox(width: 5),
                const Icon(Icons.double_arrow),
                const SizedBox(width: 5),
                Expanded(flex: 2, child: _buildButton('儲存', 0)),
              ],
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  OutlinedButton _buildButton(String text, int status) {
    // status   0:未處理    1:待處理    2:已處理
    Color color;
    VoidCallback? onPressed;

    switch (status) {
      case 0: // 未處理
        color = Colors.grey;
        onPressed = null;
        break;
      case 1: //待處理
        color = Colors.white;
        onPressed = () {};
        break;
      case 2: //已處理
        text += "\u{2611}";
        color = Colors.grey;
        onPressed = null;
        break;
      default:
        color = Colors.grey;
        onPressed = null;
        break;
    }

    return OutlinedButton(
      style: OutlinedButton.styleFrom(
        side: BorderSide(color: color),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8.0)),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      ),
      onPressed: onPressed,
      child: Text(text, style: TextStyle(color: color)),
    );
  }
}

Widget _buildInputRow(
  String label,
  String hint,
  bool enabled, {
  TextEditingController? controller,
  FocusNode? focusNode,
}) {
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 8.0),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(color: Colors.white70, fontSize: 16),
        ),
        SizedBox(
          height: 40,
          width: 250,
          child: TextField(
            focusNode: focusNode,
            controller: controller,
            enabled: enabled,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              filled: true,
              fillColor:
                  enabled
                      ? Colors.transparent
                      : const Color.fromARGB(255, 55, 56, 74),
              hintText: hint,
              hintStyle: const TextStyle(color: Colors.white54),
              border: OutlineInputBorder(
                borderSide: const BorderSide(color: Colors.red),
                borderRadius: BorderRadius.circular(8.0),
              ),
              focusedBorder: OutlineInputBorder(
                borderSide: const BorderSide(color: Colors.white),
                borderRadius: BorderRadius.circular(8.0),
              ),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 10,
              ),
            ),
          ),
        ),
      ],
    ),
  );
}
