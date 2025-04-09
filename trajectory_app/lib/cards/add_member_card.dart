import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/custom_card.dart';
import 'package:trajectory_app/models/member_model.dart';
import 'package:trajectory_app/services/api_service.dart';
import 'package:file_picker/file_picker.dart'; // 引入 file_picker
import 'dart:io'; // 用於 File 類型

class AddMemberCard extends StatefulWidget {
  final VoidCallback? onMemberAdded; // 為了更新醫生的成員數
  const AddMemberCard({super.key, this.onMemberAdded});

  @override
  State<AddMemberCard> createState() => _AddMemberCardState();
}

class _AddMemberCardState extends State<AddMemberCard> {
  final _nameController = TextEditingController();
  final _idController = TextEditingController();
  final _dateController = TextEditingController();
  final _sexController = TextEditingController();
  File? _selectedImage; // 用於儲存選擇的圖片
  //final FocusNode _textFieldFocusNode = FocusNode(); // 創建 FocusNode
  @override
  void dispose() {
    _nameController.dispose();
    _idController.dispose();
    _dateController.dispose();
    _sexController.dispose();
    //_textFieldFocusNode.dispose();
    super.dispose();
  }

  /********************************* 選擇圖片 ****************************/
  Future<void> _pickImage() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.image, // 限制只選擇圖片
      allowMultiple: false, // 僅允許單選
    );
    if (result != null && result.files.single.path != null) {
      setState(() {
        _selectedImage = File(result.files.single.path!); // 更新圖片
      });
    }
  }

  /********************************* 送出表單 ****************************/
  Future<void> _submitForm() async {
    if (_nameController.text.isEmpty ||
        _idController.text.isEmpty ||
        _dateController.text.isEmpty ||
        _sexController.text.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('請填寫所有必填欄位')));
      return;
    }
    // 解析日期
    String yyyy = '--';
    String mm = '--';
    String dd = '--';
    if (_dateController.text.isNotEmpty) {
      final dateParts = _dateController.text.split('/');
      if (dateParts.length == 3) {
        yyyy = dateParts[0];
        mm = dateParts[1];
        dd = dateParts[2];
      } else {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(const SnackBar(content: Text('日期格式錯誤，請使用 YYYY/MM/DD')));
        return;
      }
    }
    final member = MemberModel(
      name: _nameController.text,
      id: _idController.text,
      sex: _sexController.text,
      yyyy: yyyy,
      mm: mm,
      dd: dd,
    );
    // 調用 API，傳入 member 和圖片
    final success = await ApiService.memberSignup(
      member,
      _selectedImage!,
    ); // 使用 ! 斷言非空
    if (success) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('註冊成功！')));
      // 清空表單
      _nameController.clear();
      _idController.clear();
      _dateController.clear();
      _sexController.clear();
      setState(() {
        _selectedImage = null; // 清空圖片
      });
      // 更新醫生成員數量
      widget.onMemberAdded!();
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('註冊失敗，請稍後再試')));
    }
  }

  /********************************* 送出表單 ****************************/
  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return CustomCard(
      width: 425,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 50, vertical: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '新增成員',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            _buildInputRow('姓名', '姓名', true, controller: _nameController),
            _buildInputRow('身份證字號', '身份證字號', true, controller: _idController),
            _buildInputRow(
              '出生日期',
              'YYYY/MM/DD',
              true,
              controller: _dateController,
            ),
            _buildInputRow('性別', 'M/F', true, controller: _sexController),
            _buildImagePickerRow(),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(flex: 3, child: Container()),
                const SizedBox(width: 20),
                Expanded(
                  flex: 2,
                  child: OutlinedButton(
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: Colors.white),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8.0),
                      ),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 12,
                      ),
                    ),
                    onPressed: _submitForm, // 送出按鈕
                    child: const Text(
                      '送出',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImagePickerRow() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          const Text(
            '上傳照片',
            style: TextStyle(color: Colors.white70, fontSize: 16),
          ),
          SizedBox(
            height: 40,
            width: 200,
            child: OutlinedButton(
              onPressed: _pickImage, // 點擊選擇圖片
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.white), // 邊框顏色
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8.0),
                ),
                padding: const EdgeInsets.all(0), // 移除內邊距以適應內容
              ),
              child: Center(
                child:
                    _selectedImage == null
                        ? const Text(
                          '點擊選擇照片',
                          style: TextStyle(color: Colors.white54),
                        )
                        : Image.file(
                          _selectedImage!,
                          fit: BoxFit.cover,
                          height: 40,
                          width: 200,
                        ),
              ),
            ),
          ),
        ],
      ),
    );
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
            width: 200,
            child: TextField(
              focusNode: focusNode, // 綁定 FocusNode
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
}
