export const fetchChartData = async (filename) => {
  try {
    const response = await fetch(`/data/${filename}`);
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
};
