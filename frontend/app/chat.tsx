import React, { useState, useRef } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView, KeyboardAvoidingView, Platform, ActivityIndicator } from "react-native";
import { Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { Ionicons } from "@expo/vector-icons";
import { SafeAreaView } from "react-native-safe-area-context";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
}

export default function ChatScreen() {
  const { userId } = useUserStore();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { id: "1", text: "안녕하세요! 무엇이든 물어보세요. 저는 당신의 AI PT 코치입니다. 💪", sender: "ai" }
  ]);
  const [loading, setLoading] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { id: Date.now().toString(), text: input, sender: "user" };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await client.post("/api/chatbot/ask", {
        message: input,
        user_id: userId || "anonymous"
      });
      
      const aiMessage: Message = { id: (Date.now() + 1).toString(), text: response.data.answer, sender: "ai" };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage: Message = { id: (Date.now() + 1).toString(), text: "죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.", sender: "ai" };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      <Stack.Screen options={{ 
        title: "AI PT 코치 상담",
        headerShown: true,
        headerStyle: { backgroundColor: '#2563eb' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: "900" }
      }} />

      <KeyboardAvoidingView 
        behavior={Platform.OS === "ios" ? "padding" : "height"} 
        className="flex-1"
        keyboardVerticalOffset={Platform.OS === "ios" ? 90 : 0}
      >
        <ScrollView 
          ref={scrollViewRef}
          className="flex-1 p-4"
          contentContainerStyle={{ paddingBottom: 20 }}
          onContentSizeChange={() => scrollViewRef.current?.scrollToEnd({ animated: true })}
        >
          {messages.map((msg) => (
            <View 
              key={msg.id} 
              className={`mb-4 max-w-[80%] ${msg.sender === "user" ? "self-end" : "self-start"}`}
            >
              <View className={`p-4 rounded-2xl ${
                msg.sender === "user" ? "bg-blue-600 rounded-tr-none" : "bg-white rounded-tl-none shadow-sm"
              }`}>
                <Text className={`${msg.sender === "user" ? "text-white" : "text-gray-800"} text-[15px] leading-relaxed`}>
                  {msg.text}
                </Text>
              </View>
            </View>
          ))}
          {loading && (
            <View className="self-start bg-white p-4 rounded-2xl rounded-tl-none shadow-sm mb-4">
              <ActivityIndicator color="#2563eb" />
            </View>
          )}
        </ScrollView>

        <View className="p-4 bg-white border-t border-gray-100 flex-row items-center">
          <TextInput
            className="flex-1 bg-gray-100 p-4 rounded-2xl mr-3 text-[15px]"
            placeholder="궁금한 운동 지식을 물어보세요..."
            value={input}
            onChangeText={setInput}
            multiline
          />
          <TouchableOpacity 
            onPress={sendMessage}
            className={`w-12 h-12 rounded-full items-center justify-center ${input.trim() ? "bg-blue-600" : "bg-gray-200"}`}
            disabled={!input.trim()}
          >
            <Ionicons name="send" size={20} color={input.trim() ? "#fff" : "#999"} />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
