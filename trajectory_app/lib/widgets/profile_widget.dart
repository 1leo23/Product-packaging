import 'package:flutter/material.dart';
import 'package:trajectory_app/const/constant.dart';
import 'package:trajectory_app/models/manager_model.dart';
import 'package:trajectory_app/models/member_model.dart';

class ProfileWidget extends StatelessWidget {
  final String type;
  final MemberModel member;
  final ManagerModel manager;

  const ProfileWidget({
    super.key,
    required this.type,
    this.member = const MemberModel(),
    this.manager = const ManagerModel(),
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.only(left: 15, right: 15, top: 50),
      color: backgroundColor, // 深色背景
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const SizedBox(height: 20),
          const Text(
            '個人檔案',
            style: TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 20),
          Container(
            width: 180, // 直徑 = 2 * radius
            height: 180,
            padding: const EdgeInsets.all(5),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color:
                    type == 'manager'
                        ? const Color.fromARGB(255, 250, 250, 152)
                        : selectionColor, // 邊框顏色
                width: 2, // 邊框寬度
              ),
            ),
            child: const CircleAvatar(
              radius: 64, // 內部頭像略小於容器，以顯示邊框
              backgroundColor: Colors.transparent,
              backgroundImage: AssetImage('/assets/images/avatar.png'),
            ),
          ),
          const SizedBox(height: 20),

          type == 'manager' ? _managerInfo(manager) : _userInfo(member),
        ],
      ),
    );
  }
}

Column _userInfo(MemberModel member) {
  return Column(
    children: [
      Text(
        member.name,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
      const Divider(
        // 分隔線
        color: selectionColor, // 直線顏色
        thickness: 1.0, // 直線粗細
        indent: 10.0, // 左側縮進
        endIndent: 10.0, // 右側縮進
      ),
      _buildInfoRow('身分證字號', member.id),
      _buildInfoRow('出生日期', '${member.yyyy}/${member.mm}/${member.dd}'),
      _buildInfoRow('性別', member.sex),
      _buildInfoRow('影像紀錄', member.numRecords),
      const Divider(
        color: selectionColor, // 直線顏色
        thickness: 1.0, // 直線粗細
        indent: 10.0, // 左側縮進
        endIndent: 10.0, // 右側縮進
      ),
    ],
  );
}

Column _managerInfo(ManagerModel manager) {
  return Column(
    children: [
      Text(
        manager.name,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
      const Divider(
        // 分隔線
        color: selectionColor, // 直線顏色
        thickness: 1.0, // 直線粗細
        indent: 10.0, // 左側縮進
        endIndent: 10.0, // 右側縮進
      ),
      _buildInfoRow('編號', manager.id),
      _buildInfoRow('科別', manager.department),
      _buildInfoRow('成員人數', manager.numMembers),
      const Divider(
        color: selectionColor, // 直線顏色
        thickness: 1.0, // 直線粗細
        indent: 10.0, // 左側縮進
        endIndent: 10.0, // 右側縮進
      ),
    ],
  );
}

Widget _buildInfoRow(String label, String value) {
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 16.0),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: Colors.white54,
            fontWeight: FontWeight.w500,
            fontSize: 16,
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white70,
            fontWeight: FontWeight.w500,
            fontSize: 16,
          ),
        ),
      ],
    ),
  );
}
