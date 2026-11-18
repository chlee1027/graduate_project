import React, { useRef, useState } from "react";
import { ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView, Text, TextInput, TouchableOpacity, View } from "react-native";
import { Stack } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { SafeAreaView } from "react-native-safe-area-context";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { errorMessage as serverMessage } from "../src/utils/dialog";
import { colors, PlainText } from "../src/ui";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
}

const EXAMPLES = ["스쿼트할 때 무릎이 아파요", "주 3회 초보 루틴 짜 줘", "운동 전후 스트레칭 순서"];

export default function ChatScreen() {
  const { userId } = useUserStore();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<ScrollView>(null);

  const send = async (text?: string) => {
    const q = (text ?? input).trim();
    if (!q || loading) return;
    setMessages((prev) => [...prev, { id: Date.now().toString(), text: q, sender: "user" }]);
    setInput("");
    setLoading(true);
    try {
      const response = await client.post("/api/chatbot/ask", { message: q, user_id: userId || "anonymous" });
      setMessages((prev) => [...prev, { id: (Date.now() + 1).toString(), text: response.data.answer, sender: "ai" }]);
    } catch (error) {
      console.error("Chat error:", error);
      const text = serverMessage(error, "답변을 받지 못했어요. 잠시 뒤에 다시 물어봐 주세요.");
      setMessages((prev) => [...prev, { id: (Date.now() + 1).toString(), text, sender: "ai" }]);
    } finally {
      setLoading(false);
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white" edges={["bottom"]}>
      <Stack.Screen options={{ title: "코치에게 질문" }} />
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1" keyboardVerticalOffset={Platform.OS === "ios" ? 90 : 0}>
        <ScrollView
          ref={scrollRef}
          className="flex-1"
          contentContainerStyle={{ padding: 20, paddingBottom: 24 }}
          onContentSizeChange={() => scrollRef.current?.scrollToEnd({ animated: true })}
        >
          {messages.length === 0 ? (
            <View className="pt-6">
              <Text className="text-[20px] font-bold text-ink">무엇이든 물어보세요</Text>
              <Text className="text-[14px] leading-[22px] text-zinc-500 mt-2">
                운동 방법, 루틴, 통증처럼 궁금한 것을 물어보면 AI 코치가 답해요. 통증이 계속되면 전문가 진료를 받으세요.
              </Text>
              <View className="mt-6">
                {EXAMPLES.map((e) => (
                  <TouchableOpacity key={e} onPress={() => send(e)} className="py-3.5 border-b border-line flex-row justify-between items-center">
                    <Text className="text-[15px] text-ink">{e}</Text>
                    <Ionicons name="arrow-forward" size={16} color={colors.muted} />
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          ) : null}

          {messages.map((m) =>
            m.sender === "user" ? (
              <View key={m.id} className="self-end max-w-[85%] bg-ink rounded-2xl rounded-br-md px-4 py-3 mb-4">
                <Text className="text-[15px] leading-6 text-white">{m.text}</Text>
              </View>
            ) : (
              <View key={m.id} className="self-start max-w-[92%] mb-5">
                <Text className="text-[12px] font-semibold text-brand mb-1">코치</Text>
                <PlainText text={m.text} />
              </View>
            )
          )}
          {loading ? (
            <View className="self-start py-2">
              <ActivityIndicator color={colors.muted} />
            </View>
          ) : null}
        </ScrollView>

        <View className="px-4 py-3 border-t border-line flex-row items-end">
          <TextInput
            className="flex-1 min-h-[44px] max-h-32 px-4 py-3 rounded-xl border border-line text-[15px] text-ink mr-2"
            placeholder="질문을 입력하세요"
            placeholderTextColor="#A1A1AA"
            value={input}
            onChangeText={setInput}
            onSubmitEditing={() => send()}
            multiline
          />
          <TouchableOpacity
            onPress={() => send()}
            disabled={!input.trim() || loading}
            accessibilityLabel="보내기"
            className={`w-11 h-11 rounded-xl items-center justify-center ${input.trim() ? "bg-ink" : "bg-canvas"}`}
          >
            <Ionicons name="arrow-up" size={20} color={input.trim() ? "#fff" : "#A1A1AA"} />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
