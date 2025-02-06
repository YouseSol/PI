import 'dart:convert';

import 'package:http/http.dart' as http;

import 'package:pi/API/client.dart';

import 'package:pi/domain/lead.dart';


extension LeadAPIExtension on PIClient {

  Future<List<Lead>> fetchLeads(int pageSize, int page) async {
    final response = await http.get(
      Uri.parse('${baseURI}lead?page_size=$pageSize&page=$page'),
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'pi-api-token': user!.token
      }
    );

    if (response.statusCode > 299) {
      throw Exception("Failed to fetch leads.");
    }

    final leads = jsonDecode(utf8.decode(response.bodyBytes))["leads"];

    return Future.value((leads.map((m) => Lead.fromMap(m)).toList() as List<dynamic>).cast<Lead>());
  }

  Future<void> deleteLead(Lead l) async {
    final response = await http.delete(
      Uri.parse('${baseURI}lead'),
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'pi-api-token': user!.token
      },
      body: jsonEncode(l.toJson())
    );

    if (response.statusCode > 299) {
      throw Exception("Failed to delete leads.");
    }

    await Future.value();
  }

  Future<Lead> saveLead(Lead l) async {
    final response = await http.post(
      Uri.parse('${baseURI}lead'),
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'pi-api-token': user!.token
      },
      body: jsonEncode(l.toJson())
    );

    if (response.statusCode > 299) {
      throw Exception("Failed to save lead.");
    }

    return Lead.fromMap(jsonDecode(utf8.decode(response.bodyBytes)));
  }

  Future<List<Map>> fetchChatHistory(Lead l) async {
    final response = await http.get(
      Uri.parse('${baseURI}lead/${l.id}/chat'),
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'pi-api-token': user!.token
      },
    );

    if (response.statusCode > 299) {
      throw Exception("Failed to fetch chat history.");
    }

    return (jsonDecode(utf8.decode(response.bodyBytes))["messages"] as List<dynamic>).cast<Map>();
  }
}
