<template>
    <VChart
        ref="chartRef"
        class="chart"
        :manual-update="true"
        autoresize
    />
</template>

<script>
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { PieChart } from "echarts/charts";
import { TitleComponent, TooltipComponent, LegendComponent } from "echarts/components";
import VChart from "vue-echarts";
import { defineComponent, ref, onMounted } from "vue";

use([CanvasRenderer, PieChart, TitleComponent, TooltipComponent, LegendComponent]);

export default defineComponent({
    components: { VChart },

    setup() {
        const chartRef = ref(null);

        onMounted(async () => {
            await new Promise(resolve => setTimeout(resolve, 1000));

            chartRef.value.setOption({
                title: { text: "Traffic Sources", left: "center" },
                tooltip: { trigger: "item", formatter: "{a} <br/>{b} : {c} ({d}%)" },
                legend: {
                    orient: "vertical",
                    left: "left",
                    data: ["Direct", "Email", "Ad Networks", "Video Ads", "Search Engines"],
                },
                series: [
                    {
                        name: "Traffic Sources",
                        type: "pie",
                        radius: "55%",
                        center: ["50%", "60%"],
                        data: [
                            { value: 335, name: "Direct" },
                            { value: 310, name: "Email" },
                            { value: 234, name: "Ad Networks" },
                            { value: 135, name: "Video Ads" },
                            { value: 1548, name: "Search Engines" },
                        ],
                        emphasis: {
                            itemStyle: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: "rgba(0, 0, 0, 0.5)",
                            },
                        },
                    },
                ],
            });
        });

        return { chartRef };
    },
});
</script>

<style scoped>
.chart {
    height: 400px;
    width: 100%;
}
</style>
