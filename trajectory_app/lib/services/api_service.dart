import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:trajectory_app/const/constant.dart';
import 'package:trajectory_app/models/manager_model.dart';
import 'package:trajectory_app/models/member_model.dart';
import 'package:trajectory_app/services/auth_service.dart'; // 儲存中小型檔案之套件

class ApiService {
  static const String baseUrl = backendUrl; // 你的後端 API 位址

  // 獲取醫生資訊
  static Future<ManagerModel> getManagerInfo() async {
    final url = Uri.parse('$baseUrl/manager/Info');
    final token = await AuthService.getToken();

    try {
      final response = await http.post(
        url,
        body: jsonEncode({"token": token}),
        headers: {"Content-Type": "application/json"},
      );
      if (response.statusCode == 200) {
        // ✅ 確保 UTF-8 解析 JSON，防止亂碼
        final utf8DecodedBody = utf8.decode(response.bodyBytes);
        final Map<String, dynamic> data = jsonDecode(utf8DecodedBody);
        return ManagerModel.fromJson(data);
      } else {
        print("Error: ${response.statusCode} - ${response.body}");
      }
    } catch (e) {
      print("Exception: $e");
    }
    return const ManagerModel(); // 發生錯誤時回傳 null
  }

  // 獲取成員資訊
  static Future<MemberModel> getMemberInfo(String memberId) async {
    final url = Uri.parse('$baseUrl/member/Info?member_id=$memberId');
    final token = await AuthService.getToken();

    try {
      final response = await http.post(
        url,
        body: jsonEncode({"token": token}),
        headers: {"Content-Type": "application/json"},
      );
      if (response.statusCode == 200) {
        // ✅ 確保 UTF-8 解析 JSON，防止亂碼
        final utf8DecodedBody = utf8.decode(response.bodyBytes);
        final Map<String, dynamic> data = jsonDecode(utf8DecodedBody);
        return MemberModel.fromJson(data);
      } else {
        print("Error: ${response.statusCode} - ${response.body}");
      }
    } catch (e) {
      print("Exception: $e");
    }
    return const MemberModel(); // 發生錯誤時回傳 null
  }

  static Future<bool> memberSignup(MemberModel memberModel) async {
    final url = Uri.parse('$baseUrl/manager/Member_Signup');
    final token = await AuthService.getToken();

    // 將 MemberModel 轉換為 API 所需的 JSON 格式
    final Map<String, dynamic> memberData = {
      "member": {
        "id": memberModel.id,
        "sex": memberModel.sex,
        "name": memberModel.name,
        "yyyy": int.tryParse(memberModel.yyyy) ?? 0, // 轉為 int，無效時給 0
        "mm": int.tryParse(memberModel.mm) ?? 1, // 轉為 int，無效時給 1
        "dd": int.tryParse(memberModel.dd) ?? 1, // 轉為 int，無效時給 1
        "profile_image_path": "", // 預設空字串，根據需求修改
        "password": "", // 預設空字串，根據需求修改
      },
      "manager_token": {
        "token": token ?? "", // 如果 token 為 null，給空字串
      },
    };
    try {
      print(jsonEncode(memberData));
      final response = await http.post(
        url,
        body: jsonEncode(memberData),
        headers: {"Content-Type": "application/json"},
      );

      if (response.statusCode == 200) {
        // 成功註冊，使用 UTF-8 解碼回應
        final utf8DecodedBody = utf8.decode(response.bodyBytes);
        print("Member signup successful: $utf8DecodedBody");
        return true;
      } else {
        // 失敗，使用 UTF-8 解碼錯誤訊息
        final utf8DecodedError = utf8.decode(response.bodyBytes);
        print("Signup failed: ${response.statusCode} - $utf8DecodedError");
        return false;
      }
    } catch (e) {
      // 捕獲異常
      print("Exception during signup: $e");
      return false;
    }
  }

  // 新增方法：獲取會員列表
  static Future<List<MemberModel>> getMemberList() async {
    final url = Uri.parse('$baseUrl/manager/MemberList'); // 假設的端點，請根據實際情況調整
    final token = await AuthService.getToken();

    try {
      final response = await http.post(
        url,
        body: jsonEncode({"token": token}),
        headers: {"Content-Type": "application/json"},
      );

      if (response.statusCode == 200) {
        final utf8DecodedBody = utf8.decode(response.bodyBytes);
        final List<dynamic> data = jsonDecode(utf8DecodedBody);
        return data.map((json) => MemberModel.fromJson(json)).toList();
      } else {
        final utf8DecodedError = utf8.decode(response.bodyBytes);
        print(
          "Fetch member list failed: ${response.statusCode} - $utf8DecodedError",
        );
        return [];
      }
    } catch (e) {
      print("Exception during fetch member list: $e");
      return [];
    }
  }
}
