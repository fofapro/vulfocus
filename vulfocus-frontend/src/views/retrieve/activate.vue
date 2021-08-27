<template>
  <div>
    <p v-if="is_show">您的账户已经被激活</p>
  </div>
</template>

<script>
import { accessCode } from "@/api/user"
    export default {
        name: "activate",
        data() {
          return {
            is_show:false
          }
        },
        created() {
          this.geturl()
        },
        methods:{
          geturl(){
            let code = this.$route.query.code
            if (code){
              accessCode(code).then(response=>{
                let data = response.data
                if (data.code===200){
                  this.is_show=true;
                }else {
                  this.$message({
                    message: data.msg,
                    type: "error",
                  })
                  }
                })
              }else {
                this.$message({
                  message: '无效的请求',
                  type: "error",
                })
              }
        }
        },
    }
</script>

<style scoped>

</style>
