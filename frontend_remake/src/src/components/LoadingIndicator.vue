<template>
    <i class="bx bx-loader-alt loading-indicator"></i>
</template>

<style scoped>
.bx-loader-alt {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
</style>
