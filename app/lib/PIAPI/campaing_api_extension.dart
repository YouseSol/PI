import 'dart:developer';

import 'dart:convert';

import 'package:http/http.dart' as http;

import 'package:pi/PIAPI/client.dart';


extension CampaignAPIExtension on PIClient {

  Future<Map?> fetchStatusUploadedCampaign() async {
    await Future.delayed(const Duration(seconds: 3));

    final response = await http.get(
      Uri.parse('${baseURI}alessia/campaign-status'),
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'pi-api-token': user!.token
      },
    );

    if (response.statusCode > 299) {
      return null;
    }

    return jsonDecode(utf8.decode(response.bodyBytes));
  }

  void uploadCampaign(List<int> fileBytes) async {
    final request = http.MultipartRequest('POST', Uri.parse('${baseURI}alessia/activate-leads'));

    request.files.add(http.MultipartFile.fromBytes('file', fileBytes, filename: 'uploaded_file'));

    request.headers.addAll({ 'pi-api-token': user!.token });

    final response = await request.send();

    final responseBody = await http.Response.fromStream(response);
  }
}
