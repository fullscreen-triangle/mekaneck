import { useEffect } from "react";
import { useRouter } from "next/router";

export default function Sleep() {
  const router = useRouter();
  useEffect(() => { router.replace("/regimes"); }, [router]);
  return null;
}
