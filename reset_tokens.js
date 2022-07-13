// 필요한 스플렁크 자바스크립트를 import  한다. 
require([ 'jquery', 'splunkjs/mvc/simplexml/eventhandler' ], 
       // 호출되는 함수 
        function( $, EventHandler) {
                // 원하는 소스를 추가한다. 
                // reset_tokens  라는  ID를 찾아서(새로 만든 버튼) 클릭 이벤트를 추가한다. 
                $('#reset_tokens').on("click",function()
                { 
                     // stock_code 토큰을 리셋해준다. 
                     EventHandler.unsetToken("stock_code");
        });
});