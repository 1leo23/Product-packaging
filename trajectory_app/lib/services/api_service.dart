import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:trajectory_app/const/constant.dart';
import 'package:trajectory_app/models/manager_model.dart';
import 'package:trajectory_app/models/member_model.dart';
import 'package:trajectory_app/services/auth_service.dart'; // 儲存中小型檔案之套件
import 'dart:io'; // 用於 File 類型

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

  //新增成員
  static Future<bool> memberSignup(MemberModel memberModel, File image) async {
    final url = Uri.parse('$baseUrl/manager/Member_Signup');
    final token = await AuthService.getToken();

    // 創建 MultipartRequest
    var request = http.MultipartRequest('POST', url);

    // 添加表單欄位（模仿 JavaScript 的 FormData）
    request.fields['id'] = memberModel.id;
    request.fields['sex'] = memberModel.sex;
    request.fields['name'] = memberModel.name;
    request.fields['birthdate'] =
        '${memberModel.yyyy}${memberModel.mm}${memberModel.dd}'; // 格式化為 YYYYMMDD
    request.fields['managerToken'] = token ?? ''; // 如果 token 為 null，給空字串

    // 如果有圖片，添加檔案
    request.files.add(
      await http.MultipartFile.fromPath(
        'profile_image_file', // 與 JavaScript 中的鍵名一致
        image.path,
      ),
    );

    try {
      // 發送請求
      final response = await request.send();

      // 處理回應
      final responseBody = await response.stream.bytesToString(); // 將回應轉為字串
      if (response.statusCode == 200) {
        print("Member signup successful: $responseBody");
        return true;
      } else {
        print("Signup failed: ${response.statusCode} - $responseBody");
        return false;
      }
    } catch (e) {
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

  // 獲取管理者圖片 URL
  static Future<String?> getManagerImage(String managerId) async {
    final url = Uri.parse('$baseUrl/manager/profile/$managerId');
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        // ✅ 如果 API 回傳的是圖片的 URL（例如從後端 S3 或 Cloud Storage）
        return url.toString(); // 回傳圖片 URL
      } else {
        print("Manager image fetch failed: ${response.statusCode}");
      }
    } catch (e) {
      print("Exception fetching manager image: $e");
    }
    return null;
  }

  // 獲取會員圖片 URL
  static Future<String?> getMemberImage(String memberId) async {
    final url = Uri.parse('$baseUrl/member/profile/$memberId');
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        return url.toString();
      } else {
        print("Member image fetch failed: ${response.statusCode}");
      }
    } catch (e) {
      print("Exception fetching member image: $e");
    }
    return null;
  }
}
