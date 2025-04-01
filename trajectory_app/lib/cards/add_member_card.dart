import 'package:flutter/material.dart';
import 'package:trajectory_app/cards/custom_card.dart';
import 'package:trajectory_app/models/member_model.dart';
import 'package:trajectory_app/services/api_service.dart';

class AddMemberCard extends StatefulWidget {
  const AddMemberCard({super.key});

  @override
  State<AddMemberCard> createState() => _AddMemberCardState();
}

class _AddMemberCardState extends State<AddMemberCard> {
  final _nameController = TextEditingController();
  final _idController = TextEditingController();
  final _dateController = TextEditingController();

  final _sexController = TextEditingController();
  @override
  void dispose() {
    _nameController.dispose();
    _idController.dispose();
    _dateController.dispose();
    _sexController.dispose();
    super.dispose();
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

    final success = await ApiService.memberSignup(member);
    if (success) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('註冊成功！')));
      // 清空表單
      _nameController.clear();
      _idController.clear();
      _dateController.clear();
      _sexController.clear();
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('註冊失敗，請稍後再試')));
    }
  }
  /********************************* 送出表單 ****************************/

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
            _buildInputRow('上傳照片', '上傳照片', true),
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
}

Widget _buildInputRow(
  String label,
  String hint,
  bool enabled, {
  TextEditingController? controller,
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
