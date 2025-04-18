import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/custom_card.dart';
import 'package:trajectory_app/models/record_model.dart';
import 'package:trajectory_app/services/api_service.dart';
import 'package:loading_animation_widget/loading_animation_widget.dart';

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
  final _mmseController = TextEditingController();
  final _actualAgeController = TextEditingController();
  final _brainAgeController = TextEditingController();
  final _riskScoreController = TextEditingController();
  File? _selectedFile;
  bool _isProcessing = false;

  void dispose() {
    _idController.dispose();
    _idFocusNode.dispose();
    _dateController.dispose();
    _mmseController.dispose();
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

  int _uploadStatus = 1; // 0=未處理, 1=可處理, 2=已完成
  int _aiStatus = 0;
  int _saveStatus = 0;
  Future<void> _handleUploadRecord() async {
    setState(() {
      _isProcessing = true;
    });

    try {
      print("開始建檔");
      final memberId = _idController.text.trim();
      final rawDate = _dateController.text.trim();
      final mmseScoreText = _mmseController.text.trim();
      final mmseScore = int.tryParse(mmseScoreText);

      // === 基本欄位驗證 ===
      if (memberId.isEmpty || rawDate.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("請填寫完整的 身份證字號 / 拍攝日期 "),
            backgroundColor: Colors.redAccent,
          ),
        );
        return;
      }

      // === 日期格式驗證與轉換 ===
      final dateRegExp = RegExp(r'^\d{4}/\d{2}/\d{2}$');
      if (!dateRegExp.hasMatch(rawDate)) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("拍攝日期格式錯誤，請使用 YYYY/MM/DD 格式"),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }

      final parts = rawDate.split('/');
      final formattedDate = '${parts[0]}${parts[1]}${parts[2]}';

      final file = _selectedFile;
      if (file == null || !await file.exists()) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("請選擇有效的 NIfTI 檔案 (.nii.gz)"),
            backgroundColor: Colors.redAccent,
          ),
        );
        return;
      }

      final result = await ApiService.uploadRecord(
        memberId: memberId,
        date: formattedDate,
        niiFile: file,
        mmseScore: mmseScore,
      );

      if (result) {
        final List<RecordModel> records = await ApiService.getMemberRecordList(
          memberId,
        );
        String actualAge = '';
        if (records.isNotEmpty) {
          actualAge = records.last.actualAge;
          print('實際年齡：$actualAge');
        }

        setState(() {
          _uploadStatus = 2;
          _aiStatus = 1;
          _actualAgeController.text = actualAge;
          _idController.text = memberId;
          _dateController.text = rawDate;
          _mmseController.text =
              mmseScore == null ? "未做認知測驗" : mmseScore.toString();
        });

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("✅ 建檔完成，可進行 AI 預測"),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("❌ 建檔失敗，請檢查輸入與伺服器狀態"),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      // 保證在任何情況下都會結束「處理中」
      setState(() {
        _isProcessing = false;
      });
    }
  }

  Future<void> _handleAiPrediction() async {
    setState(() {
      _isProcessing = true;
    });
    try {
      final memberId = _idController.text.trim();
      // === 驗證欄位 ===
      if (memberId.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("請輸入成員身分證字號"),
            backgroundColor: Colors.redAccent,
          ),
        );
        return;
      }

      // === 呼叫 API 取得 record_count ===
      final memberInfo = await ApiService.getMemberInfo(memberId);
      final int recordCount = int.tryParse(memberInfo.numRecords) ?? -1;
      if (recordCount <= 0) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("⚠️ 該成員尚無任何紀錄"),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }

      // === 呼叫 AI 推論 API ===
      final result = await ApiService.runAiPrediction(
        memberId: memberId,
        recordCount: recordCount,
      );

      if (result != null) {
        setState(() {
          _aiStatus = 2;
          _saveStatus = 1;
          _brainAgeController.text = result['brainAge'].toString();
          _riskScoreController.text = result['riskScore'].toString();
        });

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("✅ AI 預測成功"),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("❌ AI 預測失敗，請稍後再試"),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isProcessing = false;
      });
    }
  }

  Future<void> _handleSaveSlices() async {
    setState(() {
      _isProcessing = true;
    });
    try {
      final memberId = _idController.text.trim();
      // === 呼叫 API 取得 record_count ===
      final memberInfo = await ApiService.getMemberInfo(memberId);
      final int recordCount = int.tryParse(memberInfo.numRecords) ?? -1;
      if (recordCount <= 0) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("⚠️ 該成員尚無任何紀錄"),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }
      // === 驗證欄位 ===
      if (memberId.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("請輸入成員身分證字號"),
            backgroundColor: Colors.redAccent,
          ),
        );
        return;
      }
      if (recordCount <= 0) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("無效的紀錄編號"),
            backgroundColor: Colors.orange,
          ),
        );
        return;
      }

      final result = await ApiService.sliceAndStoreMRI(
        memberId: memberId,
        recordCount: recordCount,
      );

      if (result) {
        setState(() {
          _saveStatus = 2;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("✅ 切片與儲存完成"),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("❌ 切片失敗，請檢查檔案與紀錄狀態"),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isProcessing = false;
      });
    }
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
              _uploadStatus != 2,
              controller: _idController,
              focusNode: _idFocusNode,
            ), // 如果已經建檔成功，就鎖住此欄位
            _buildInputRow(
              '拍攝日期',
              'YYYY/MM/DD',
              controller: _dateController,
              _uploadStatus != 2,
            ), // 如果已經建檔成功，就鎖住此欄位
            _buildFilePickerRow(
              '上傳檔案',
              '選擇檔案 (.nii.gz)',
              _uploadStatus != 2,
            ), // 如果已經建檔成功，就鎖住此欄位
            _buildInputRow(
              '認知測驗',
              '1 ~ 100 (可不填寫)',
              controller: _mmseController,
              _uploadStatus != 2,
            ), // 如果已經建檔成功，就鎖住此欄位
            _buildInputRow(
              '實際年齡',
              '實際年齡 (自動填入)',
              controller: _actualAgeController,
              false,
            ),
            _buildInputRow(
              '腦部年齡',
              '腦部年齡 (AI計算)',
              controller: _brainAgeController,
              false,
            ),
            _buildInputRow(
              '失智症風險',
              '失智症風險 (AI計算)',
              controller: _riskScoreController,
              false,
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  flex: 2,
                  child: _buildButton('建檔', _uploadStatus, _handleUploadRecord),
                ),
                const SizedBox(width: 5),
                const Icon(Icons.double_arrow),
                const SizedBox(width: 5),
                Expanded(
                  flex: 2,
                  child: _buildButton('AI計算', _aiStatus, _handleAiPrediction),
                ),
                const SizedBox(width: 5),
                const Icon(Icons.double_arrow),
                const SizedBox(width: 5),
                Expanded(
                  flex: 2,
                  child: _buildButton('儲存', _saveStatus, _handleSaveSlices),
                ),
              ],
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  OutlinedButton _buildButton(
    String text,
    int status,
    VoidCallback? onPressed,
  ) {
    // status   0:未處理    1:待處理    2:已處理
    Color color;
    Widget buttonChild;
    if (_isProcessing && status == 1) {
      onPressed = null;
      color = Colors.grey;
      buttonChild = LoadingAnimationWidget.staggeredDotsWave(
        color: Colors.white,
        size: 20,
      );
      // 如果程序正在處理中 待處理的按鈕暫時變為disable
    } else {
      switch (status) {
        case 0: // 未處理
          color = Colors.grey;
          onPressed = null;
          break;
        case 1: //待處理
          color = Colors.white;
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
      buttonChild = Text(text, style: TextStyle(color: color));
    }

    return OutlinedButton(
      style: OutlinedButton.styleFrom(
        side: BorderSide(color: color),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8.0)),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      ),
      onPressed: onPressed,
      child: buttonChild,
    );
  }

  Widget _buildFilePickerRow(String label, String hint, bool enabled) {
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
            child: OutlinedButton(
              onPressed:
                  enabled
                      ? () async {
                        FilePickerResult? result = await FilePicker.platform
                            .pickFiles(
                              type: FileType.custom,
                              allowedExtensions: ['nii', 'gz', 'nii.gz'],
                            );
                        if (result != null &&
                            result.files.single.path != null) {
                          setState(() {
                            _selectedFile = File(result.files.single.path!);
                          });
                        }
                      }
                      : null,
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.white),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8.0),
                ),
                padding: const EdgeInsets.all(0),
              ),
              child: Text(
                _selectedFile == null
                    ? hint
                    : '✅ ${_selectedFile!.path.split(Platform.pathSeparator).last}',
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: Colors.white54),
              ),
            ),
          ),
        ],
      ),
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
