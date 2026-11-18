import React, { useState } from "react";
import { Text, TouchableOpacity } from "react-native";
import { Stack, useRouter } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { errorMessage } from "../src/utils/dialog";
import { Button, Field, Screen, Title } from "../src/ui";

export default function Login() {
  const router = useRouter();
  const { setSession } = useUserStore();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!username.trim() || !password) return setError("아이디와 비밀번호를 입력해 주세요.");
    setError(null);
    setLoading(true);
    try {
      const r = await client.post("/api/auth/login", { username: username.trim(), password });
      setSession({ userId: r.data.user_id, username: r.data.username, token: r.data.token });
      router.replace("/");
    } catch (e) {
      setError(errorMessage(e, "로그인하지 못했어요. 잠시 뒤에 다시 시도해 주세요."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen footer={<Button label="로그인" onPress={submit} loading={loading} />}>
      <Stack.Screen options={{ title: "로그인" }} />
      <Title sub="다른 기기에서 쓰던 기록을 그대로 이어서 볼 수 있어요.">로그인</Title>
      <Field label="아이디" value={username} onChange={setUsername} onSubmit={submit} />
      <Field label="비밀번호" value={password} onChange={setPassword} secure onSubmit={submit} error={error} />
      <TouchableOpacity onPress={() => router.replace("/onboarding")} className="py-2">
        <Text className="text-[14px] text-zinc-500">계정이 없어요 · 새로 시작하기</Text>
      </TouchableOpacity>
    </Screen>
  );
}
