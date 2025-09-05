package com.example.test;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
public class TestOnLongClickActivity extends AppCompatActivity {
    TextView textView;
    Button button;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_test);
    
        initViews();
        initListener();}
    public void onButtonClick() {
        // 点击事件
        textView.setText("Button clicked!");
    }
    @OnLongClick(R.id.text_view)
    public boolean onTextViewLongClick(View view) {
        // 长按事件
        textView.setText("TextView long clicked!");
        return true;
    }

    protected void initViews() {
        // 初始化View绑定 - 替换@BindView注解
        textView = findViewById(R.id.text_view);
        button = findViewById(R.id.button);
    }

    public void initListener() {
        // 初始化点击事件 - 替换@OnClick注解
        findViewById(R.id.button).setOnClickListener(v -> onButtonClick());
        // 初始化长按事件 - 替换@OnLongClick注解
        findViewById(R.id.text_view).setOnLongClickListener(v -> onTextViewLongClick(v));
    }
}