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
import { LineChart } from "echarts/charts";
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from "echarts/components";
import VChart from "vue-echarts";
import { defineComponent, ref, watch, onMounted } from "vue";
import { formatTimestamp, formatDate } from "@/utils/utils";

use([CanvasRenderer, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent]);

export default defineComponent({
    name: "ChartLine",
    components: { VChart },
    props: {
        chartData: {
            type: Array,
            required: true
        }
    },
    setup(props) {
        const chartRef = ref(null);

        const updateChart = (data) => {
            // Group data by metric_name
            const seriesMap = {};
            console.log(data)
            data.forEach(item => {
                // Use metric_name + element_id as the key for grouping
                const key = `${item.metric_name} (#${item.element_id})`;
                if (!seriesMap[key]) seriesMap[key] = [];
                seriesMap[key].push({ value: item.value, time: item.created_at });
            });

            const series = Object.entries(seriesMap).map(([label, items]) => ({
                name: label,
                type: "line",
                smooth: true,
                data: items.map(i => [i.time, i.value])   // <— pair the time with the value
            }));

            console.log(series)

            chartRef.value.setOption({
                tooltip: {
                    trigger: "axis",
                    formatter: params => {
                        const time = params[0].axisValue;
                        const rows = params.map(p => `
                            <div style="display:flex; justify-content:space-between; gap:32px;">
                                <span>${p.marker} ${p.seriesName}</span>
                                <span">${p.data[1].toLocaleString("fi-FI")}</span>
                            </div>`).join("");

                        return `
                            <div style="font-size: var(--fs-2); font-weight: var(--fw-semibold); color: var(--text-dark-primary); padding-bottom: 4px">
                                ${formatTimestamp(time)}
                            </div>
                            <div style="display:flex; flex-direction:column; gap:2px;">
                                ${rows}
                            </div>`;
                    },
                    borderWidth: 0,
                    extraCssText: `
                        box-shadow: var(--shadow-md);
                        color: var(--text-dark-secondary);
                        font-weight: var(--fw-medium);
                        font-size: var(--fs-1);
                        border-radius: 8px;
                        padding: 10px 12px;
                    `
                },

                textStyle: {
                    fontFamily: "Inter",
                    fontSize: "0.75rem",
                    fontWeight: "500"
                },

                legend: { data: Object.keys(seriesMap), top: 0 },
                grid: { top: 32, bottom: 0, left: 0, right: 8 },

                color: [
                    'hsl(210, 50%, 30%)',
                    'hsl(105, 57%, 55%)',
                    'hsl(47, 100%, 71%)',
                    'hsl(0, 75%, 65%)',
                    'hsl(190, 43%, 66%)',
                    'hsl(165, 54%, 44%)',
                    'hsl(24, 82%, 61%)',
                    'hsl(260, 45%, 58%)',
                    'hsl(335, 57%, 73%)'
                ],

                xAxis: {
                    type: "time",
                    axisLabel: {
                        formatter: (value) => formatDate(value),
                        rotate: 45,
                        fontSize: "0.75rem",
                        color: "hsl(0, 0%, 45%)"
                    },
                    axisLine: { show: false },
                    axisTick: { show: false }
                },

                yAxis: {
                    type: "value",
                    axisLabel: {
                        formatter: (v) => v.toLocaleString("fi-FI"),
                        fontSize: "0.75rem",
                        color: "hsl(0, 0%, 45%)", // --text-dark-secondary
                    }
                },

                series
            });
        };

        onMounted(() => {
            if (props.chartData.length) updateChart(props.chartData);
        });

        watch(() => props.chartData, (newData) => {
            if (newData.length) updateChart(newData);
        });

        return { chartRef };
    }
});
</script>

<style scoped>
.chart {
    height: 400px;
    width: 100%;
}
</style>
