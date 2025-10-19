<template>
    <div class="data-view">
        <h1>Data</h1>
        <p>Data goes here</p>
    </div>
</template>

<script>

export default {
    name: 'DataView',
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

.data-view h1 {
    font-size: var(--fs-8);
    font-weight: var(--fw-bold);
    color: var(--text-dark-primary);
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-500));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.data-view p {
    font-size: var(--fs-3);
    color: var(--text-dark-secondary);
    line-height: 1.6;
    margin-top: 1rem;
}
</style>
