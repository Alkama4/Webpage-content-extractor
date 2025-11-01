<template>
    <div class="data-view">
        <h1>Data</h1>
        <p>Data goes here</p>
        <ChartLine/>
    </div>
</template>

<script>
import ChartLine from '@/components/ChartLine.vue';

export default {
    name: 'DataView',
    components: {
        ChartLine,
    },
    data() {
        return {

        };
    },
    methods: {

    },
    async mounted() {

    },
};
</script>

<style scoped>
.data-view {
    max-width: 1200px;
    margin: 0 auto;
}
</style>
