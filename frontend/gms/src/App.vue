<template>
  <div id="app" :class="!silent ? '' : 'silent'">
    <router-view v-if="isRouterAlive"></router-view>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  provide() {
    return {
      reload: this.reload,
    };
  },
  data() {
    return {
      isRouterAlive: true,
    };
  },
  methods: {
    reload() {
      this.isRouterAlive = false;
      this.$nextTick(function () {
        this.isRouterAlive = true;
      });
    },
    getSilent() {
      axios.get('/api/sms/user/getSilent').then(response => {
        const data = response.data;
        this.$store.commit('SAVE_SILENT', data);
      });
    },
  },
  mounted() {
    this.getSilent();
  },
  computed: {
    silent() {
      return this.$store.state.silent;
    },
  },
};
</script>

<style>

</style>
