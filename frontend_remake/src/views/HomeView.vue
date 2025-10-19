<template>
    <div class="home-view">
        <h1>Welcome!</h1>
        <p>Placholder</p>
    </div>
</template>

<script>

export default {
    name: 'HomeView',
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
.home-view {
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
    padding: 4rem 2rem;
}

.home-view h1 {
    font-size: var(--fs-10);
    font-weight: var(--fw-bold);
    color: var(--text-dark-primary);
    margin-bottom: 1rem;
    background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-500));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.home-view p {
    font-size: var(--fs-3);
    color: var(--text-dark-secondary);
    line-height: 1.6;
}
</style>
