import { Alert, Platform } from "react-native";

// react-native-web 의 Alert.alert 는 아무것도 띄우지 않는다. 웹에서는 브라우저 대화상자를 쓴다.

export function notify(title: string, message?: string): void {
  if (Platform.OS === "web") {
    window.alert(message ? `${title}\n\n${message}` : title);
  } else {
    Alert.alert(title, message);
  }
}

export function confirmAction(
  title: string,
  message: string,
  confirmText: string,
  onConfirm: () => void,
  cancelText = "취소",
): void {
  if (Platform.OS === "web") {
    if (window.confirm(`${title}\n\n${message}`)) onConfirm();
    return;
  }
  Alert.alert(title, message, [
    { text: cancelText, style: "cancel" },
    { text: confirmText, style: "destructive", onPress: onConfirm },
  ]);
}

// 서버가 보낸 안내(예: 호출 제한 429)가 있으면 그것을, 없으면 기본 문구를 쓴다.
export function errorMessage(error: any, fallback: string): string {
  const detail = error?.response?.data?.detail;
  return typeof detail === "string" ? detail : fallback;
}
