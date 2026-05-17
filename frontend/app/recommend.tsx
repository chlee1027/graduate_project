import React, { useState, useEffect } from "react";
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator, Alert, Linking } from "react-native";
import { useRouter, Stack } from "expo-router";
import { useUserStore } from "../src/store/userStore";
import client from "../src/api/client";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";

export default function Recommend() {
  const router = useRouter();
  const { userId } = useUserStore();
  const [loading, setLoading] = useState(true);
  const [recommendation, setRecommendation] = useState<any>(null);
  const [location, setLocation] = useState<"gym" | "home">("gym");
  const [wantStretching, setWantStretching] = useState(false);

  const fetchRecommendation = async (currentLocation: "gym" | "home", stretching: boolean = false) => {
    setLoading(true);
    try {
      const response = await client.post("/api/recommend/", {
        user_id: userId,
        location: currentLocation,
        available_minutes: 60,
        fatigue: 2,
        sleep_hours: 7.0,
        recent_adherence_7d: 0.8,
        streak: null, // Let backend calculate
        avg_rpe_last_7d: 5.0,
        want_stretching: stretching,
      });
      setRecommendation(response.data);
    } catch (error) {
      console.error(error);
      Alert.alert("오류", "추천을 불러오지 못했습니다. 서버 상태나 네트워크를 확인해주세요.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchRecommendation(location, wantStretching);
    } else {
      setLoading(false);
      Alert.alert("오류", "사용자 정보가 없습니다. 온보딩을 먼저 진행해주세요.");
      router.replace("/onboarding");
    }
  }, [userId]);

  const handleLocationChange = (newLoc: "gym" | "home") => {
    setLocation(newLoc);
    fetchRecommendation(newLoc, wantStretching);
  };

  const toggleStretching = () => {
    const nextValue = !wantStretching;
    setWantStretching(nextValue);
    fetchRecommendation(location, nextValue);
  };

  if (loading) {
    return (
      <View className="flex-1 justify-center items-center">
        <ActivityIndicator size="large" color="#2563eb" />
        <Text className="mt-4 text-gray-500">
          AI가 {wantStretching ? "회복" : location === "gym" ? "헬스장" : "홈트"} 맞춤 플랜을 찾고 있습니다...
        </Text>
      </View>
    );
  }

  const getThemeColors = () => {
    if (wantStretching) {
      return {
        bg: '#f0fdf4', // emerald-50
        border: '#dcfce7', // emerald-100
        accent: '#059669', // emerald-600
        text: '#064e3b', // emerald-900
        button: '#10b981', // emerald-500
        label: "액티브 레스트"
      };
    }

    const intensity = recommendation.selected_plan.intensity;
    if (location === 'gym') {
      // 헬스장: 파란색 계열
      if (intensity === 'low') {
        return { bg: '#eff6ff', border: '#dbeafe', accent: '#3b82f6', text: '#1e3a8a', button: '#3b82f6', label: "오늘의 플랜" };
      } else if (intensity === 'medium') {
        return { bg: '#dbeafe', border: '#bfdbfe', accent: '#2563eb', text: '#1e3a8a', button: '#2563eb', label: "오늘의 플랜" };
      } else { // high
        return { bg: '#bfdbfe', border: '#93c5fd', accent: '#1d4ed8', text: '#1e3a8a', button: '#1d4ed8', label: "오늘의 플랜" };
      }
    } else {
      // 홈트: 연두/초록색 계열
      if (intensity === 'low') {
        return { bg: '#f7fee7', border: '#ecfccb', accent: '#65a30d', text: '#365314', button: '#84cc16', label: "오늘의 플랜" };
      } else if (intensity === 'medium') {
        return { bg: '#ecfccb', border: '#d9f99d', accent: '#4d7c0f', text: '#365314', button: '#65a30d', label: "오늘의 플랜" };
      } else { // high
        return { bg: '#d9f99d', border: '#bef264', accent: '#3f6212', text: '#1a2e05', button: '#4d7c0f', label: "오늘의 플랜" };
      }
    }
  };

  const theme = recommendation ? getThemeColors() : null;

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ 
        title: "오늘의 추천", 
        headerShown: true,
        headerStyle: { backgroundColor: '#2563eb' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: "900", fontSize: 18 },
        headerShadowVisible: false,
        headerLeft: () => (
          <TouchableOpacity 
            onPress={() => router.back()} 
            className="ml-3 w-10 h-10 items-center justify-center rounded-full active:opacity-60"
          >
            <Ionicons name="chevron-back" size={28} color="#fff" style={{ marginLeft: -3 }} />
          </TouchableOpacity>
        )
      }} />
      <ScrollView className="p-6 pt-4" showsVerticalScrollIndicator={false}>
        <View className="mb-8">
          <Text className="text-3xl font-black text-gray-900">오늘의 추천</Text>
          <Text className="text-gray-400 font-bold text-xs uppercase mt-1">당신에게 가장 적합한 루틴을 제안합니다</Text>
        </View>

        <View className="flex-row bg-gray-100 p-1.5 rounded-3xl mb-8">
          <TouchableOpacity
            onPress={() => handleLocationChange("gym")}
            className={`flex-1 py-3 rounded-2xl items-center ${location === "gym" ? "bg-white shadow-sm" : ""}`}
          >
            <Text className={`font-black text-xs ${location === "gym" ? "text-blue-600" : "text-gray-400"}`}>🏋️ 헬스장</Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={() => handleLocationChange("home")}
            className={`flex-1 py-3 rounded-2xl items-center ${location === "home" ? "bg-white shadow-sm" : ""}`}
          >
            <Text className={`font-black text-xs ${location === "home" ? "text-blue-600" : "text-gray-400"}`}>🏠 홈트</Text>
          </TouchableOpacity>
        </View>

        {recommendation && theme ? (
          <>
            <View 
              style={{ backgroundColor: theme.bg, borderColor: theme.border }}
              className="p-8 rounded-[40px] border mb-8"
            >
              <View className="flex-row justify-between items-start mb-6">
                <View>
                  <Text style={{ color: theme.accent }} className="text-[10px] font-black uppercase tracking-widest mb-1">
                    {theme.label}
                  </Text>
                  <Text style={{ color: theme.text }} className="text-2xl font-black">
                    {recommendation.selected_plan.name}
                  </Text>
                </View>
                <View style={{ backgroundColor: theme.accent }} className="px-3 py-1 rounded-full">
                  <Text className="text-white font-bold text-[10px]">{recommendation.selected_plan.intensity.toUpperCase()}</Text>
                </View>
              </View>
              
              <View className="flex-row mb-8">
                <View className="mr-8">
                  <Text className="text-gray-400 text-[10px] font-bold uppercase mb-1">예상 시간</Text>
                  <Text className="text-gray-900 font-black text-lg">{recommendation.selected_plan.minutes}분</Text>
                </View>
                <View>
                  <Text className="text-gray-400 text-[10px] font-bold uppercase mb-1">{recommendation.selected_plan.type === 'time-based' ? '유형' : '세트/횟수'}</Text>
                  <Text className="text-gray-900 font-black text-lg">
                    {recommendation.selected_plan.type === 'time-based' ? '지속 수행' : `${recommendation.selected_plan.sets}세트 × ${recommendation.selected_plan.reps}회`}
                  </Text>
                </View>
              </View>

              {recommendation.selected_plan.video_url && (
                <TouchableOpacity
                  onPress={() => Linking.openURL(recommendation.selected_plan.video_url)}
                  className="bg-white/80 py-4 rounded-2xl flex-row items-center justify-center border border-white shadow-sm active:opacity-90"
                >
                  <Text style={{ color: theme.accent }} className="font-black text-sm">
                    📺 가이드 영상 보기
                  </Text>
                </TouchableOpacity>
              )}
            </View>

            {wantStretching && (
              <View className="bg-emerald-50 p-4 rounded-2xl border border-emerald-100 mb-6 flex-row items-center">
                <Text className="text-xl mr-3">💡</Text>
                <Text className="text-emerald-800 text-[10px] font-bold flex-1">
                  스트레칭은 '회복 세션'입니다.{"\n"}성실한 운동 데이터 축적을 위해 주간 목표 횟수에는 포함되지 않아요!
                </Text>
              </View>
            )}

            <TouchableOpacity
              style={{ backgroundColor: theme.button }}
              className="p-5 rounded-3xl items-center shadow-lg mb-4 active:opacity-90"
              onPress={() => router.push({
                pathname: `/workout/${recommendation.selected_plan.plan_id}`,
                params: { recommendation_id: recommendation.recommendation_id }
              })}
            >
              <Text className="text-white font-black text-lg">운동 시작하기</Text>
            </TouchableOpacity>

            <TouchableOpacity
              onPress={toggleStretching}
              className="py-4 items-center mb-4"
            >
              <Text className={`font-black text-xs ${wantStretching ? "text-blue-600" : "text-gray-400"}`}>
                {wantStretching ? "↻ 원래 추천 플랜으로 돌아가기" : "오늘은 좀 몸이 무거워요... (스트레칭) 🧘"}
              </Text>
            </TouchableOpacity>
          </>
        ) : (
          <View className="p-10 items-center">
            <Text className="text-gray-400">추천 결과가 없습니다.</Text>
          </View>
        )}
        
        <TouchableOpacity
          className="p-4 items-center bg-gray-50 rounded-2xl mx-10 border border-gray-100"
          onPress={() => fetchRecommendation(location, wantStretching)}
        >
          <Text className="text-blue-600 font-bold text-[10px]">다른 추천 받기 ↻</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
