<script>
	import Loading from  './Loading.svelte'

	export let api;

</script>
	<section>
<aside>
	<button on:click={() => api.build()}>Build</button>
</aside>
	</section>